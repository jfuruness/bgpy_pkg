import pytest

from bgpy.as_graphs import ASGraph, ASGraphInfo, CustomerProviderLink as CPLink


class TestGetCustomerConeSize:

    def test_stub_as_cone_size_is_zero(self):
        graph = ASGraph(
            ASGraphInfo(customer_provider_links=frozenset([
                CPLink(provider_asn=1, customer_asn=2)
            ])),
            store_customer_cone_size=True,
        )
        assert graph.as_dict[2].stub is True
        assert graph.as_dict[2].customer_cone_size == 0

    def test_multihomed_as_cone_size_is_zero(self):
        graph = ASGraph(
            ASGraphInfo(customer_provider_links=frozenset([
                CPLink(provider_asn=1, customer_asn=3),
                CPLink(provider_asn=2, customer_asn=3),
            ])),
            store_customer_cone_size=True,
        )
        assert graph.as_dict[3].multihomed is True
        assert graph.as_dict[3].customer_cone_size == 0

    def test_unlinked_as_cone_size_is_zero(self):
        graph = ASGraph(
            ASGraphInfo(unlinked_asns=frozenset([99])),
            store_customer_cone_size=True,
        )
        assert graph.as_dict[99].customer_cone_size == 0

    # Testing topology

    def test_transit_with_one_stub_customer(self):
        """
        Topology: AS1 -> AS2 -> AS3

        AS1 -> customer_cone_size = 2
        AS2 -> customer_cone_size = 1
        AS3 -> customer_cone_size = 0
        """
        graph = ASGraph(
            ASGraphInfo(customer_provider_links=frozenset([
                CPLink(provider_asn=1, customer_asn=2),
                CPLink(provider_asn=2, customer_asn=3),
            ])),
            store_customer_cone_size=True,
        )
        assert graph.as_dict[1].stub is True
        assert graph.as_dict[1].customer_cone_size == 2
        assert graph.as_dict[2].customer_cone_size == 1
        assert graph.as_dict[3].stub is True
        assert graph.as_dict[3].customer_cone_size == 0

    def test_provider_with_two_stub_customers(self):
        """
        Topology: AS1 -> AS2, AS1 -> AS3

        AS 1 has AS2, AS3 so customer_cone size is 2
        """
        graph = ASGraph(
            ASGraphInfo(customer_provider_links=frozenset([
                CPLink(provider_asn=1, customer_asn=2),
                CPLink(provider_asn=1, customer_asn=3),
            ])),
            store_customer_cone_size=True,
        )
        assert graph.as_dict[1].customer_cone_size == 2

    def test_diamond_no_double_counting(self):
        """
        Topology(diamond): AS1 -> AS2, AS1 -> AS3
                           AS2 -> AS4, AS3 -> AS4

        AS1 -> customer_cone_size = 3 (AS4 is counted once as it should)
        AS2 -> customer_cone_size = 1
        AS3 -> customer_cone_size = 1
        AS4 -> customer_cone_size = 0
        """
        graph = ASGraph(
            ASGraphInfo(customer_provider_links=frozenset([
                CPLink(provider_asn=1, customer_asn=2),
                CPLink(provider_asn=1, customer_asn=3),
                CPLink(provider_asn=2, customer_asn=4),
                CPLink(provider_asn=3, customer_asn=4),
            ])),
            store_customer_cone_size=True,
        )
        assert graph.as_dict[4].multihomed is True
        assert graph.as_dict[4].customer_cone_size == 0
        assert graph.as_dict[2].customer_cone_size == 1
        assert graph.as_dict[3].customer_cone_size == 1
        assert graph.as_dict[1].customer_cone_size == 3

    def test_two_providers_one_shared_multihomed_customer(self):
        """
        Topology: AS1 -> AS3, AS2 -> AS3

        AS1 -> customer_cone_size = 1
        AS2 -> customer_cone_size = 1
        AS3 -> customer_cone_size = 0

        """
        graph = ASGraph(
            ASGraphInfo(customer_provider_links=frozenset([
                CPLink(provider_asn=1, customer_asn=3),
                CPLink(provider_asn=2, customer_asn=3),
            ])),
            store_customer_cone_size=True,
        )
        assert graph.as_dict[3].multihomed is True
        assert graph.as_dict[3].customer_cone_size == 0
        assert graph.as_dict[1].customer_cone_size == 1
        assert graph.as_dict[2].customer_cone_size == 1

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
        graph = ASGraph(
            ASGraphInfo(customer_provider_links=frozenset([
                CPLink(provider_asn=1, customer_asn=2),
                CPLink(provider_asn=1, customer_asn=3),
                CPLink(provider_asn=2, customer_asn=4),
                CPLink(provider_asn=2, customer_asn=5),
                CPLink(provider_asn=3, customer_asn=5),
                CPLink(provider_asn=3, customer_asn=6),
            ])),
            store_customer_cone_size=True,
        )
        assert graph.as_dict[5].multihomed is True
        assert graph.as_dict[5].customer_cone_size == 0
        assert graph.as_dict[4].customer_cone_size == 0
        assert graph.as_dict[6].customer_cone_size == 0
        assert graph.as_dict[2].customer_cone_size == 2
        assert graph.as_dict[3].customer_cone_size == 2
        assert graph.as_dict[1].customer_cone_size == 5
        assert graph.as_dict[1].customer_cone_size == 5
