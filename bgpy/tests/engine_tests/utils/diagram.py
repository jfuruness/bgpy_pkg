from graphviz import Digraph
import ipaddress

from bgpy.enums import Outcomes
from bgpy.simulation_engine import BGPAS
from bgpy.simulation_engine import BGPSimpleAS


class Diagram:
    def __init__(self):
        self.dot = Digraph(format="png")
        # purple is cooler but I guess that's not paper worthy
        # self.dot.attr(bgcolor='purple:pink')

    def generate_as_graph(
        self,
        engine,
        scenario,
        traceback,
        description,
        metric_tracker,
        diagram_ranks,
        static_order: bool = False,
        path=None,
        view=False,
    ):
        self._add_legend(traceback)
        self._add_ases(engine, traceback, scenario)
        self._add_edges(engine)
        self._add_diagram_ranks(diagram_ranks, static_order)
        # https://stackoverflow.com/a/57461245/8903959
        self.dot.attr(label=description)
        self._render(path=path, view=view)

    def _add_legend(self, traceback):
        """Adds legend to the graph with outcome counts"""

        attacker_success_count = sum(
            1 for x in traceback.values() if x == Outcomes.ATTACKER_SUCCESS
        )
        victim_success_count = sum(
            1 for x in traceback.values() if x == Outcomes.VICTIM_SUCCESS
        )
        disconnect_count = sum(
            1 for x in traceback.values() if x == Outcomes.DISCONNECTED
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
            </TABLE>>"""

        kwargs = {"color": "black", "style": "filled", "fillcolor": "white"}
        self.dot.node("Legend", html, shape="plaintext", **kwargs)

    def _add_ases(self, engine, traceback, scenario):
        # First add all nodes to the graph
        for as_obj in engine:
            self._encode_as_obj_as_node(self.dot, as_obj, engine, traceback, scenario)

    def _encode_as_obj_as_node(self, subgraph, as_obj, engine, traceback, scenario):
        kwargs = dict()
        # if False:
        #     kwargs = {"style": "filled,dashed",
        #               "shape": "box",
        #               "color": "black",
        #               "fillcolor": "lightgray"}
        html = self._get_html(as_obj, engine, scenario)

        kwargs = self._get_kwargs(as_obj, engine, traceback, scenario)

        subgraph.node(str(as_obj.asn), html, **kwargs)

    def _get_html(self, as_obj, engine, scenario):
        asn_str = str(as_obj.asn)
        if as_obj.asn in scenario.victim_asns:
            asn_str = "&#128519;" + asn_str + "&#128519;"
        elif as_obj.asn in scenario.attacker_asns:
            asn_str = "&#128520;" + asn_str + "&#128520;"

        html = f"""<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
            <TR>
            <TD COLSPAN="4" BORDER="0">{asn_str}</TD>
            </TR>
            <TR>
            <TD COLSPAN="4" BORDER="0">({as_obj.name})</TD>
            </TR>"""
        local_rib_anns = tuple(list(as_obj._local_rib._info.values()))
        local_rib_anns = tuple(
            sorted(
                local_rib_anns,
                key=lambda x: ipaddress.ip_network(x.prefix).num_addresses,
                reverse=True,
            )
        )
        if len(local_rib_anns) > 0:
            html += """<TR>
                        <TD COLSPAN="4">Local RIB</TD>
                      </TR>"""

            for ann in local_rib_anns:
                mask = "/" + ann.prefix.split("/")[-1]
                path = ", ".join(str(x) for x in ann.as_path)
                ann_help = ""
                if getattr(ann, "blackhole", False):
                    ann_help = "&#10041;"
                elif getattr(ann, "preventive", False):
                    ann_help = "&#128737;"
                elif any(x in ann.as_path for x in scenario.attacker_asns):
                    ann_help = "&#128520;"
                elif any(x == ann.origin for x in scenario.victim_asns):
                    ann_help = "&#128519;"
                else:
                    raise Exception(f"Not valid ann for rib? {ann}")

                html += f"""<TR>
                            <TD>{mask}</TD>
                            <TD>{path}</TD>
                            <TD>{ann_help}</TD>
                          </TR>"""
        html += "</TABLE>>"
        return html

    def _get_kwargs(self, as_obj, engine, traceback, scenario):
        kwargs = {
            "color": "black",
            "style": "filled",
            "fillcolor": "white",
            "gradientangle": "270",
        }

        # If the as obj is the attacker
        if as_obj.asn in scenario.attacker_asns:
            kwargs.update({"fillcolor": "#ff6060", "shape": "doublecircle"})
            if as_obj.__class__ not in (BGPAS, BGPSimpleAS):
                kwargs["shape"] = "doubleoctagon"
            # If people complain about the red being too dark lol:
            kwargs.update({"fillcolor": "#FF7F7F"})
            # kwargs.update({"fillcolor": "#ff4d4d"})
        # As obj is the victim
        elif as_obj.asn in scenario.victim_asns:
            kwargs.update({"fillcolor": "#90ee90", "shape": "doublecircle"})
            if as_obj.__class__ not in (BGPAS, BGPSimpleAS):
                kwargs["shape"] = "doubleoctagon"

        # As obj is not attacker or victim
        else:
            if traceback[as_obj.asn] == Outcomes.ATTACKER_SUCCESS:
                kwargs.update({"fillcolor": "#ff6060:yellow"})
            elif traceback[as_obj.asn] == Outcomes.VICTIM_SUCCESS:
                kwargs.update({"fillcolor": "#90ee90:white"})
            elif traceback[as_obj.asn] == Outcomes.DISCONNECTED:
                kwargs.update({"fillcolor": "grey:white"})

            if as_obj.__class__ not in [BGPAS, BGPSimpleAS]:
                kwargs["shape"] = "octagon"
        return kwargs

    def _add_edges(self, engine):
        # Then add all connections to the graph
        # Starting with provider to customer
        for as_obj in engine:
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
                    )

    def _add_diagram_ranks(self, diagram_ranks, static_order: bool):
        # TODO: Refactor
        if static_order is False:
            for i, rank in enumerate(diagram_ranks):
                g = Digraph(f"Propagation_rank_{i}")
                g.attr(rank="same")
                for as_obj in rank:
                    g.node(str(as_obj.asn))
                self.dot.subgraph(g)
        else:
            for i, rank in enumerate(diagram_ranks):
                with self.dot.subgraph() as s:
                    s.attr(rank="same")  # set all nodes to the same rank
                    previous_asn = None
                    for as_obj in rank:
                        asn = str(as_obj.asn)
                        s.node(asn)
                        if previous_asn is not None:
                            # Add invisible edge to maintain static order
                            s.edge(previous_asn, asn, style="invis")  # type: ignore
                        previous_asn = asn

    def _render(self, path=None, view=False):
        self.dot.render(path, view=view)
