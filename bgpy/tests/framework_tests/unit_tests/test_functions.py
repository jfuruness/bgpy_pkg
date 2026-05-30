import pytest

from bgpy.as_graphs import ASGraph, ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink


def build_graph(*cp_links: CPLink, unlinked_asns: frozenset[int] = frozenset()) -> ASGraph:
    """Builds a graph that we can use to test the specific cone sizes"""
    info = ASGraphInfo(
        customer_provider_links=frozenset(cp_links),
        unlinked_asns=unlinked_asns,
    )
    return ASGraph(info, store_customer_cone_size=True)


class TestGetCustomerConeSize:

    def test_stub_as_cone_size_is_zero(self):
        """Test that cone_size is zero"""
        graph = build_graph(CPLink(provider_asn=1, customer_asn=2))
        assert graph.as_dict[2].stub is True
        assert graph.as_dict[2].customer_cone_size == 0

    def test_multihomed_as_cone_size_is_zero(self):
        """Test that multihomed cone_size is zero"""
        graph = build_graph(
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=2, customer_asn=3),
        )
        assert graph.as_dict[3].multihomed is True
        assert graph.as_dict[3].customer_cone_size == 0

    def test_unlinked_as_cone_size_is_zero(self):
        """Tests that unlinked ASN have a cone_size of zero"""
        graph = build_graph(unlinked_asns=frozenset([99]))
        assert graph.as_dict[99].customer_cone_size == 0

    # Testing topology
    # Important: An AS with a neighbor of 1 is still considered a stub, so their cone size is zero
    # essentially, you need move a node above and below for the customer_cone_size to not be zero
    # customer_cone_size gets only the nodes below the current AS 

    def test_transit_with_one_stub_customer(self):
        """
        Topology: AS1 -> AS2 -> AS3

        AS1 -> customer_cone_size = 0
        AS2 -> customer_cone_size = 1
        AS3 -> customer_cone_size = 0
        """
        graph = build_graph(
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=2, customer_asn=3),
        )
        assert graph.as_dict[1].stub is True
        assert graph.as_dict[1].customer_cone_size == 0
        assert graph.as_dict[2].customer_cone_size == 1
        assert graph.as_dict[3].stub is True
        assert graph.as_dict[3].customer_cone_size == 0

    def test_provider_with_two_stub_customers(self):
        """
        Topology: AS1 -> AS2, AS1 -> AS3

        AS 1 has AS2, AS3 so customer_cone size is 2
        """
        graph = build_graph(
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=1, customer_asn=3),
        )
        assert graph.as_dict[1].customer_cone_size == 2

    def test_four_level_chain(self):
        """
        Topology: AS1 -> AS2 -> AS3 -> AS4

        AS1 -> customer_cone_size = 0
        AS2 -> customer_cone_size = 2
        AS3 -> customer_cone_size = 1
        AS4 -> customer_cone_size = 0
        """
        graph = build_graph(
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=2, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=4),
        )
        assert graph.as_dict[1].customer_cone_size == 0   
        assert graph.as_dict[2].customer_cone_size == 2   
        assert graph.as_dict[3].customer_cone_size == 1   
        assert graph.as_dict[4].customer_cone_size == 0   

    def test_diamond_no_double_counting(self):
        """
        Topology(diamond): AS1 -> AS2, AS1 -> AS3
                           AS2 -> AS4, AS3 -> AS4
        
        AS1 -> customer_cone_size = 3 (AS4 is counted once as it should)
        AS2 -> customer_cone_size = 1
        AS3 -> customer_cone_size = 1
        AS4 -> customer_cone_size = 0
        """
        graph = build_graph(
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=2, customer_asn=4),
            CPLink(provider_asn=3, customer_asn=4),
        )
        assert graph.as_dict[4].multihomed is True
        assert graph.as_dict[4].customer_cone_size == 0
        assert graph.as_dict[2].customer_cone_size == 1
        assert graph.as_dict[3].customer_cone_size == 1
        assert graph.as_dict[1].customer_cone_size == 3

    def test_two_providers_one_shared_multihomed_customer(self):
        """
        Topology: AS1 -> AS3, AS2 -> AS3

        AS1 -> customer_cone_size = 0
        AS2 -> customer_cone_size = 0
        AS3 -> customer_cone_size = 0
        
        AS1 and AS2 are considered stubs so customer_cone_size = 0
        """
        graph = build_graph(
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=2, customer_asn=3),
        )
        assert graph.as_dict[3].multihomed is True
        assert graph.as_dict[3].customer_cone_size == 0
        assert graph.as_dict[1].stub is True
        assert graph.as_dict[1].customer_cone_size == 0
        assert graph.as_dict[2].stub is True
        assert graph.as_dict[2].customer_cone_size == 0


    def test_three_tier_topology(self):
        """
        Topology: AS1 -> AS2, AS3
                  AS2 -> AS4, AS5
                  AS3 -> AS5, AS6

        AS1 -> customer_cone_size = 5
        AS2 -> customer_cone_size = 2
        AS3 -> customer_cone_size = 2
        Rest of AS are zero
        """
        graph = build_graph(
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=2, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=5),
            CPLink(provider_asn=3, customer_asn=5),
            CPLink(provider_asn=3, customer_asn=6),
        )
        assert graph.as_dict[5].multihomed is True
        assert graph.as_dict[5].customer_cone_size == 0
        assert graph.as_dict[4].customer_cone_size == 0
        assert graph.as_dict[6].customer_cone_size == 0
        assert graph.as_dict[2].customer_cone_size == 2
        assert graph.as_dict[3].customer_cone_size == 2
        assert graph.as_dict[1].customer_cone_size == 5
