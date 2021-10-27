from graphviz import Digraph
import ipaddress

from ...engine import BGPAS, BGPSimpleAS
from ...enums import Outcomes

class Diagram:
    def __init__(self):
        self.dot = Digraph(format="png")
        # purple is cooler imo but whatever
        # self.dot.attr(bgcolor='purple:pink')

    def generate_as_graph(self, *args, path=None, view=False):
        self._add_legend(*args)
        self._add_ases(*args)
        self._add_edges(*args)
        self._add_propagation_ranks(*args)
        self._add_as_types(*args)
        self._add_traceback_types(*args)
        self.render(path=path, view=view)

    def render(self, path=None, view=False):
        self.dot.render(path, view=view)

    def _add_ases(self, engine, traceback, engine_input, *args):
        # First add all nodes to the graph
        for as_obj in engine:
            self.encode_as_obj_as_node(self.dot,
                                       as_obj,
                                       engine,
                                       traceback,
                                       engine_input,
                                       *args)
    def _add_legend(self, engine, traceback, *args):

        attacker_success_count = sum(1 for x in traceback.values() if x == Outcomes.ATTACKER_SUCCESS)
        victim_success_count = sum(1 for x in traceback.values() if x == Outcomes.VICTIM_SUCCESS)
        disconnect_count = sum(1 for x in traceback.values() if x == Outcomes.DISCONNECTED)
        html = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                      <TR>
                        <TD BGCOLOR="red:yellow">&#128520; ATTACKER SUCCESS &#128520;</TD>
                        <TD>{attacker_success_count}</TD>
                      </TR>
                      <TR>
                        <TD BGCOLOR="green:white">&#128519; VICTIM SUCCESS &#128519;</TD>
                        <TD>{victim_success_count}</TD>
                      </TR>
                      <TR>
                        <TD BGCOLOR="grey:white">&#10041; DISCONNECTED &#10041;</TD>
                        <TD>{disconnect_count}</TD>
                      </TR>
                    </TABLE>>'''

        kwargs = {"color": "black", "style": "filled", "fillcolor": "white"}
        self.dot.node("Legend", html, shape="plaintext", **kwargs)

    def encode_as_obj_as_node(self,
                              subgraph,
                              as_obj,
                              engine,
                              traceback,
                              engine_input,
                              *args):
        kwargs = dict()
        if False:
            kwargs = {"style": "filled,dashed",
                      "shape": "box",
                      "color": "black",
                      "fillcolor": "lightgray"}
        html = self._get_html(as_obj,
                              engine,
                              traceback,
                              engine_input,
                              *args)

        kwargs = self._get_kwargs(as_obj,
                                  engine,
                                  traceback,
                                  engine_input,
                                  *args)

        subgraph.node(str(as_obj.asn), html, **kwargs)

    def _add_edges(self, engine, *args):
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
                    self.dot.edge(str(as_obj.asn), str(peer_obj.asn), dir="none")

    def _add_propagation_ranks(self, engine, *args):
        for i, rank in enumerate(engine.propagation_ranks):
            g = Digraph(f"Propagation_rank_{i}")
            g.attr(rank="same")
            for as_obj in rank:

                g.node(str(as_obj.asn))
            self.dot.subgraph(g)

    def _add_as_types(self, engine, *args):
        pass

    def _add_traceback_types(self, engine, *args):
        pass

    def _get_html(self, as_obj, engine, traceback, engine_input, *args):
        asn_str = str(as_obj.asn)
        if as_obj.asn == engine_input.victim_asn:
            asn_str = "&#128519;" + asn_str + "&#128519;"
        elif as_obj.asn == engine_input.attacker_asn:
            asn_str = "&#128520;" + asn_str + "&#128520;"

        html = f"""<
                    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                      <TR>
                        <TD COLSPAN="3" BORDER="0">{asn_str}</TD>
                      </TR>
                      <TR>
                        <TD COLSPAN="3" BORDER="0">({as_obj.name})</TD>
                      </TR>"""
        if as_obj.asn not in engine_input.uncountable_asns and False:
            outcome = traceback[as_obj.asn]
            if outcome == Outcomes.ATTACKER_SUCCESS:
                outcome_str = "&#128520; ATTACKER SUCCESS &#128520;"
            elif outcome == Outcomes.VICTIM_SUCCESS:
                outcome_str = "&#128519; VICTIM SUCCESS &#128519;"
            elif outcome == Outcomes.DISCONNECTED:
                outcome_str = "&#10041; DISCONNECTED &#10041;"
            html += f"""<TR>
                        <TD COLSPAN="3">{outcome_str}</TD>
                      </TR>"""
        html += """<TR>
                    <TD COLSPAN="3">Local RIB</TD>
                  </TR>"""
        local_rib_prefixes = list(as_obj._local_rib._info.keys())
        local_rib_prefixes = tuple(sorted(local_rib_prefixes,
                                           key=lambda x: ipaddress.ip_network(x).num_addresses,
                                           reverse=True))
        for prefix in local_rib_prefixes:
            mask = "/" + prefix.split("/")[-1]
            path = ", ".join(str(x) for x in as_obj._local_rib._info[prefix].as_path)
            html += f"""<TR>
                        <TD>{mask}</TD>
                        <TD>{path}</TD>
                      </TR>"""
        html += "</TABLE>>"
        return html

    def _get_kwargs(self, as_obj, engine, traceback, engine_input, *args):
        kwargs = {"color": "black", "style": "filled", "fillcolor": "white"}

        # If the as obj is the attacker
        if as_obj.asn == engine_input.attacker_asn:
            kwargs.update({"fillcolor": "red", "shape": "doublecircle"})
            if as_obj.__class__ not in [BGPAS, BGPSimpleAS]:
                kwargs["shape"] = "doubleoctagon"
            # If people complain about the red being too dark lol:
            kwargs.update({"fillcolor": "#FF7F7F"})
            # kwargs.update({"fillcolor": "#ff4d4d"})
        # As obj is the victim
        elif as_obj.asn == engine_input.victim_asn:
            kwargs.update({"fillcolor": "green", "shape": "doublecircle"})
            if as_obj.__class__ not in [BGPAS, BGPSimpleAS]:
                kwargs["shape"] = "doubleoctagon"

        # As obj is not attacker or victim
        else:
            if traceback[as_obj.asn] == Outcomes.ATTACKER_SUCCESS:
                kwargs.update({"fillcolor": "red:yellow"})
            elif traceback[as_obj.asn] == Outcomes.VICTIM_SUCCESS:
                kwargs.update({"fillcolor": "green:white"})
            elif traceback[as_obj.asn] == Outcomes.DISCONNECTED:
                kwargs.update({"fillcolor": "grey:white"})

            if as_obj.__class__ not in [BGPAS, BGPSimpleAS]:
                kwargs["shape"] = "octagon"
        return kwargs
