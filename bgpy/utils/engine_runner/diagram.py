import ipaddress
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING

from graphviz import Digraph

from bgpy.shared.enums import Outcomes
from bgpy.simulation_engine import BGP, BaseSimulationEngine, BGPFull
from bgpy.simulation_framework import Scenario

if TYPE_CHECKING:
    from bgpy.as_graphs.base.as_graph import AS
    from bgpy.simulation_framework.graph_data_aggregator import GraphDataAggregator


class Diagram:
    """Creates a diagram of an AS graph with traceback"""

    def __init__(self) -> None:
        self.dot: Digraph = Digraph(format="png")
        # purple is cooler but I guess that's not paper worthy
        # self.dot.attr(bgcolor='purple:pink')

    def generate_as_graph(
        self,
        engine: BaseSimulationEngine,
        scenario: Scenario,
        # Just the data plane
        traceback: dict[int, int],
        description: str,
        graph_data_aggregator: "GraphDataAggregator",
        diagram_ranks: tuple[tuple["AS", ...], ...],
        static_order: bool = False,
        path: Path | None = None,
        view: bool = False,
        dpi: int | None = None,
    ) -> None:
        self._add_legend(traceback, scenario)
        display_next_hop_asn = self._display_next_hop_asn(engine, scenario)
        self._add_ases(engine, traceback, scenario, display_next_hop_asn)
        self._add_edges(engine)
        # Always recompute diagram rows from the engine's AS-graph relationships.
        # The passed-in diagram_ranks may use the propagation convention (leaves
        # at index 0) or may contain Rule-1 violations; recomputing here
        # guarantees Rule 1 (provider strictly above customer) and Rule 2
        # (peers share a row when safe).  static_order still controls whether
        # invisible horizontal-ordering edges are added within each rank.
        diagram_ranks = self._compute_diagram_rows(engine)
        self._add_diagram_ranks(diagram_ranks, static_order)
        self._add_description(description, display_next_hop_asn)
        self._render(path=path, view=view, dpi=dpi)

    # ------------------------------------------------------------------
    # Row-assignment helpers
    # ------------------------------------------------------------------

    def _compute_diagram_rows(
        self, engine: BaseSimulationEngine
    ) -> tuple[tuple["AS", ...], ...]:
        """Return diagram rows satisfying two invariants.

        Rule 1 (hard): every provider sits in a strictly smaller row index than
        every one of its customers.  Row 0 is the top of the diagram (root
        providers); higher indices are further down.

        Rule 2 (soft): peers share a row when doing so does not violate Rule 1
        for any node in the graph.  When the constraint cannot be satisfied the
        peer edge simply crosses rows; it is never allowed to break Rule 1.
        """
        as_graph = engine.as_graph
        as_dict: dict[int, AS] = {a.asn: a for a in as_graph}

        # --- Step 1: longest-path-from-root via Kahn's topological sort -------
        # Each node's row = length of the longest provider-customer chain from
        # any root provider down to that node.  Using Kahn's algorithm ensures
        # every provider is fully settled before we update its customers, so
        # each customer always receives the true maximum depth.
        rows: dict[int, int] = {a.asn: 0 for a in as_graph}
        in_degree: dict[int, int] = {a.asn: len(a.providers) for a in as_graph}

        # Seed the queue with root nodes (no providers) — these are row 0.
        queue: deque[AS] = deque(a for a in as_graph if not a.providers)

        while queue:
            node = queue.popleft()
            for customer in node.customers:
                # Rule 1: customer must be at least one row below this provider.
                rows[customer.asn] = max(
                    rows[customer.asn], rows[node.asn] + 1
                )
                in_degree[customer.asn] -= 1
                if in_degree[customer.asn] == 0:
                    queue.append(customer)

        # --- Step 2: peer alignment (Rule 2, soft constraint) -----------------
        # For each peer pair try to place them on the same row.  Only move a
        # node when every one of its provider-customer constraints remains
        # strictly satisfied after the move.
        seen: set[tuple[int, int]] = set()
        for as_obj in as_graph:
            for peer in as_obj.peers:
                key = (min(as_obj.asn, peer.asn), max(as_obj.asn, peer.asn))
                if key in seen:
                    continue
                seen.add(key)

                if rows[as_obj.asn] == rows[peer.asn]:
                    continue  # already aligned

                # Try moving `peer` to `as_obj`'s row, then the reverse.
                # Use _peer_move_safe rather than _row_change_safe so we also
                # refuse to move a node away from a row where it is already
                # aligned with another peer (prevents the greedy pass from
                # breaking prior alignments in peer triangles).
                if self._peer_move_safe(peer.asn, rows[as_obj.asn], rows, as_dict):
                    rows[peer.asn] = rows[as_obj.asn]
                elif self._peer_move_safe(
                    as_obj.asn, rows[peer.asn], rows, as_dict
                ):
                    rows[as_obj.asn] = rows[peer.asn]
                # else: leave them on different rows; cross-row peer edges are
                # drawn as dashed lines and do not violate any invariant.

        # --- Assemble into tuple-of-tuples ------------------------------------
        max_row = max(rows.values(), default=0)
        buckets: list[list[AS]] = [[] for _ in range(max_row + 1)]
        for as_obj in as_graph:
            buckets[rows[as_obj.asn]].append(as_obj)
        return tuple(tuple(sorted(group)) for group in buckets)

    def _row_change_safe(
        self,
        asn: int,
        new_row: int,
        rows: dict[int, int],
        as_dict: dict[int, "AS"],
    ) -> bool:
        """Return True if assigning *new_row* to *asn* keeps Rule 1 intact.

        Rule 1 requires every provider to occupy a strictly smaller row index
        than every one of its customers (row 0 = top of the diagram).
        """
        as_obj = as_dict[asn]
        # Every provider must remain strictly above this node.
        for provider in as_obj.providers:
            if rows[provider.asn] >= new_row:
                return False
        # Every customer must remain strictly below this node.
        return all(rows[customer.asn] > new_row for customer in as_obj.customers)

    def _peer_move_safe(
        self,
        asn: int,
        new_row: int,
        rows: dict[int, int],
        as_dict: dict[int, "AS"],
    ) -> bool:
        """Return True if moving *asn* to *new_row* is safe for peer alignment.

        A move is safe when it satisfies Rule 1 (via _row_change_safe) AND
        does not de-align any peer that is already on the same row as *asn*.
        Without this second check a greedy pass over peer pairs can move a
        floating node into alignment with one peer while breaking a prior
        alignment with another (classic peer-triangle problem: if A-B are both
        at row 0 and C is at row 2, processing pair (B, C) must not move B to
        row 2 and silently break the A-B alignment).
        """
        if not self._row_change_safe(asn, new_row, rows, as_dict):
            return False
        # Refuse to vacate the current row if another peer is already there.
        current_row = rows[asn]
        return all(rows[peer.asn] != current_row for peer in as_dict[asn].peers)

    def _add_legend(self, traceback: dict[int, int], scenario: Scenario) -> None:
        """Adds legend to the graph with outcome counts"""

        attacker_success_count = sum(
            1 for x in traceback.values() if x == Outcomes.ATTACKER_SUCCESS.value
        )
        victim_success_count = sum(
            1 for x in traceback.values() if x == Outcomes.VICTIM_SUCCESS.value
        )
        disconnect_count = sum(
            1 for x in traceback.values() if x == Outcomes.DISCONNECTED.value
        )
        html = f"""<
              <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
              <TR>
          <TD COLSPAN="2" BORDER="0">(For most specific prefix only)</TD>
              </TR>
              <TR>
          <TD BGCOLOR="#ff6060:white">&#128520; ATTACKER SUCCESS &#128520;</TD>
                <TD>{attacker_success_count}</TD>
              </TR>
              <TR>
         <TD BGCOLOR="#90ee90:white">&#128519; VICTIM SUCCESS &#128519;</TD>
                <TD>{victim_success_count}</TD>
              </TR>
              <TR>
                <TD BGCOLOR="grey:white">&#10041; DISCONNECTED &#10041;</TD>
                <TD>{disconnect_count}</TD>
              </TR>
        """

        # ROAs takes up the least space right underneath the legend
        # which is why we have this here instead of a separate node
        html += """
              <TR>
                <TD COLSPAN="2" BORDER="0">ROAs (prefix, origin, max_len)</TD>
              </TR>
              """
        for roa in scenario.roas:
            html += f"""
              <TR>
                <TD>{roa.prefix}</TD>
                <TD>{roa.origin}</TD>
                <TD>{roa.max_length}</TD>
              </TR>"""
        html += """</TABLE>>"""

        kwargs = {"color": "black", "style": "filled", "fillcolor": "white"}
        self.dot.node("Legend", html, shape="plaintext", **kwargs)

    def _display_next_hop_asn(
        self, engine: BaseSimulationEngine, scenario: Scenario
    ) -> bool:
        """Displays the next hop ASN

        We want to display the next hop ASN any time it has been manipulated
        That only happens when the next_hop_asn is not equal to the as object's ASN
        (which occurs when the AS is the origin) or the next ASN in the path
        """

        for as_obj in engine.as_graph:
            for ann in as_obj.policy.local_rib.values():
                if (len(ann.as_path) == 1 and ann.as_path[0] != ann.next_hop_asn) or (
                    len(ann.as_path) > 1 and ann.as_path[1] != ann.next_hop_asn
                ):
                    return True
        return False

    def _add_ases(
        self,
        engine: BaseSimulationEngine,
        traceback: dict[int, int],
        scenario: Scenario,
        display_next_hop_asn: bool,
    ) -> None:
        # First add all nodes to the graph
        for as_obj in engine.as_graph:
            self._encode_as_obj_as_node(
                self.dot, as_obj, engine, traceback, scenario, display_next_hop_asn
            )

    def _encode_as_obj_as_node(
        self,
        subgraph: Digraph,
        as_obj: "AS",
        engine: BaseSimulationEngine,
        traceback: dict[int, int],
        scenario: Scenario,
        display_next_hop_asn: bool,
    ) -> None:
        kwargs = dict()
        # if False:
        #     kwargs = {"style": "filled,dashed",
        #               "shape": "box",
        #               "color": "black",
        #               "fillcolor": "lightgray"}
        html = self._get_html(as_obj, engine, scenario, display_next_hop_asn)

        kwargs = self._get_kwargs(as_obj, engine, traceback, scenario)

        subgraph.node(str(as_obj.asn), html, **kwargs)

    def _get_html(
        self,
        as_obj: "AS",
        engine: BaseSimulationEngine,
        scenario: Scenario,
        display_next_hop_asn: bool,
    ) -> str:
        colspan = 5 if display_next_hop_asn else 4
        asn_str = str(as_obj.asn)
        if as_obj.asn in scenario.victim_asns:
            asn_str = "&#128519;" + asn_str + "&#128519;"
        elif as_obj.asn in scenario.attacker_asns:
            asn_str = "&#128520;" + asn_str + "&#128520;"

        html = f"""<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="{colspan}">
            <TR>
            <TD COLSPAN="{colspan}" BORDER="0">{asn_str}</TD>
            </TR>
            <TR>
            <TD COLSPAN="{colspan}" BORDER="0">({as_obj.policy.name})</TD>
            </TR>"""
        local_rib_anns = tuple(as_obj.policy.local_rib.values())
        local_rib_anns = tuple(
            sorted(
                local_rib_anns,
                key=lambda x: ipaddress.ip_network(x.prefix).num_addresses,
                reverse=True,
            )
        )
        if len(local_rib_anns) > 0:
            html += f"""<TR>
                        <TD COLSPAN="{colspan}">Local RIB</TD>
                      </TR>"""

            for ann in local_rib_anns:
                mask = "/" + ann.prefix.split("/")[-1]
                path = ", ".join(str(x) for x in ann.as_path)
                ann_help = ""
                if getattr(ann, "rovpp_blackhole", False):
                    ann_help = "&#10041;"
                elif getattr(ann, "preventive", False):
                    ann_help = "&#128737;"
                elif any(x in ann.as_path for x in scenario.attacker_asns):
                    ann_help = "&#128520;"
                elif any(x == ann.origin for x in scenario.victim_asns):
                    ann_help = "&#128519;"
                else:
                    raise NotImplementedError

                html += f"""<TR>
                            <TD>{mask}</TD>
                            <TD>{path}</TD>
                            <TD>{ann_help}</TD>"""
                if display_next_hop_asn:
                    html += f"""<TD>{ann.next_hop_asn}</TD>"""
                html += """</TR>"""
        html += "</TABLE>>"
        return html

    def _get_kwargs(
        self,
        as_obj: "AS",
        engine: BaseSimulationEngine,
        traceback: dict[int, int],
        scenario: Scenario,
    ) -> dict[str, str]:
        kwargs = {
            "color": "black",
            "style": "filled",
            "fillcolor": "white",
            "gradientangle": "270",
        }

        # If the as obj is the attacker
        if as_obj.asn in scenario.attacker_asns:
            kwargs.update({"fillcolor": "#ff6060", "shape": "doublecircle"})
            if as_obj.policy.__class__ not in (BGPFull, BGP):
                kwargs["shape"] = "doubleoctagon"
            # If people complain about the red being too dark lol:
            kwargs.update({"fillcolor": "#FF7F7F"})
            # kwargs.update({"fillcolor": "#ff4d4d"})
        # As obj is the victim
        elif as_obj.asn in scenario.victim_asns:
            kwargs.update({"fillcolor": "#90ee90", "shape": "doublecircle"})
            if as_obj.policy.__class__ not in (BGPFull, BGP):
                kwargs["shape"] = "doubleoctagon"

        # As obj is not attacker or victim
        else:
            if traceback[as_obj.asn] == Outcomes.ATTACKER_SUCCESS.value:
                kwargs.update({"fillcolor": "#ff6060:yellow"})
            elif traceback[as_obj.asn] == Outcomes.VICTIM_SUCCESS.value:
                kwargs.update({"fillcolor": "#90ee90:white"})
            elif traceback[as_obj.asn] == Outcomes.DISCONNECTED.value:
                kwargs.update({"fillcolor": "grey:white"})

            if as_obj.policy.__class__ not in [BGPFull, BGP]:
                kwargs["shape"] = "octagon"
        return kwargs

    def _add_edges(self, engine: BaseSimulationEngine):
        # Then add all connections to the graph
        # Starting with provider to customer
        for as_obj in engine.as_graph:
            # Add provider customer edges
            for customer_obj in as_obj.customers:
                self.dot.edge(str(as_obj.asn), str(customer_obj.asn))
            # Add peer edges
            # Only add if the largest asn is the curren as_obj to avoid dups
            for peer_obj in as_obj.peers:
                if as_obj.asn > peer_obj.asn:
                    self.dot.edge(
                        str(as_obj.asn),
                        str(peer_obj.asn),
                        dir="none",
                        style="dashed",
                        penwidth="2",
                        # Peer edges must not affect Graphviz rank (vertical
                        # placement).  Without constraint=false a peer edge
                        # A->B creates a hidden rank constraint rank(B)≥rank(A)+1
                        # which can contradict the provider-customer hierarchy
                        # and cause directed cycles that flip PC arrows upward.
                        constraint="false",
                    )

    def _add_diagram_ranks(
        self, diagram_ranks: tuple[tuple["AS", ...], ...], static_order: bool
    ) -> None:
        # TODO: Refactor
        if static_order is False:
            for i, rank in enumerate(diagram_ranks):
                g = Digraph(f"Propagation_rank_{i}")
                g.attr(rank="same")
                for as_obj in rank:
                    g.node(str(as_obj.asn))
                self.dot.subgraph(g)
        else:
            for rank in diagram_ranks:
                with self.dot.subgraph() as s:
                    s.attr(rank="same")  # set all nodes to the same rank
                    previous_asn: str | None = None
                    for as_obj in rank:
                        asn = str(as_obj.asn)
                        s.node(asn)
                        if previous_asn is not None:
                            # Add invisible edge to maintain static order
                            s.edge(previous_asn, asn, style="invis")
                        previous_asn = asn

    def _add_description(self, description: str, display_next_hop_asn: bool) -> None:
        if display_next_hop_asn:
            description += (
                "\nLocal RIB rows displayed as: prefix, as path, origin, next_hop"
            )
        # https://stackoverflow.com/a/57461245/8903959
        self.dot.attr(label=description)

    def _render(
        self, path: Path | None = None, view: bool = False, dpi: int | None = None
    ) -> None:
        if dpi:
            self.dot.attr(dpi=str(dpi))
        self.dot.render(path, view=view)
