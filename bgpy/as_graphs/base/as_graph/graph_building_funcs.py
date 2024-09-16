"""Gontains functions needed to build graph and it's references"""

from typing import TYPE_CHECKING
from weakref import proxy

from .base_as import AS

if TYPE_CHECKING:
    from bgpy.as_graphs import ASGraphInfo
    from bgpy.simulation_engine import Policy


def _gen_graph(
    self,
    as_graph_info: "ASGraphInfo",
    BaseASCls: type[AS],
    BasePolicyCls: type["Policy"],
):
    """Generates a graph of AS objects"""

    def _gen_as(asn):
        as_ = BaseASCls(
            asn=asn,
            policy=BasePolicyCls(),
            as_graph=self,
        )
        assert as_.policy.as_ == proxy(
            as_
        ), f"{BaseASCls} not setting policy.as_ correctly"
        # Monkey patching these in here whilst generating the AS graph
        as_.peers_setup_set = set()
        as_.customers_setup_set = set()
        as_.providers_setup_set = set()
        return as_

    # Add all links to the graph
    for asn in as_graph_info.asns:
        # AS dict is not yet frozen, type ignore
        self.as_dict[asn] = self.as_dict.get(asn, _gen_as(asn))

    # Add all IXPs to the graph
    for asn in as_graph_info.ixp_asns:
        # AS dict is not yet frozen, type ignore
        self.as_dict[asn] = self.as_dict.get(asn, _gen_as(asn))
        if asn in self.as_dict:
            self.as_dict[asn].ixp = True

    # Add all input cliques to the graph
    for asn in as_graph_info.input_clique_asns:
        # AS dict is not yet frozen, type ignore
        self.as_dict[asn] = self.as_dict.get(asn, _gen_as(asn))
        self.as_dict[asn].input_clique = True


def _add_relationships(self, as_graph_info: "ASGraphInfo") -> None:
    """Adds relationships to the graph as references

    NOTE: we monkey patch peers_setup_set while the AS Graph is being generated
    for speed
    """

    for cp_link in as_graph_info.customer_provider_links:
        # Extract customer and provider obj
        customer = self.as_dict[cp_link.customer_asn]
        provider = self.as_dict[cp_link.provider_asn]
        # Store references
        customer.providers_setup_set.add(provider)
        provider.customers_setup_set.add(customer)

    for peer_link in as_graph_info.peer_links:
        # Extract as objects for peers
        asn1, asn2 = peer_link.asns
        p1, p2 = self.as_dict[asn1], self.as_dict[asn2]
        # Add references to peers
        p1.peers_setup_set.add(p2)
        p2.peers_setup_set.add(p1)


def _make_relationships_tuples(self):
    """Make relationships tuples

    NOTE: we monkey patch peers_setup_set while the AS Graph is being generated
    for speed
    """

    rel_attrs = ("peers", "providers", "customers")
    setup_rel_attrs = ("peers_setup_set", "providers_setup_set", "customers_setup_set")

    for as_obj in self:
        for rel_attr, setup_rel_attr in zip(rel_attrs, setup_rel_attrs, strict=False):
            # Conver the setup attribute to tuple
            # Must be sorted or else yaml dumps differently
            sorted_ases = sorted(getattr(as_obj, setup_rel_attr), key=lambda x: x.asn)
            setattr(as_obj, rel_attr, tuple([proxy(x) for x in sorted_ases]))
            asns_attr = rel_attr[:-1] + "_asns"
            setattr(as_obj, asns_attr, frozenset([x.asn for x in sorted_ases]))

            # Delete the setup attribute
            delattr(as_obj, setup_rel_attr)
