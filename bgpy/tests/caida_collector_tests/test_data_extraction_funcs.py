from pathlib import Path

import pytest

from bgpy.caida_collector import CaidaCollector
from bgpy.caida_collector import CustomerProviderLink as CPLink, PeerLink


@pytest.mark.data_extraction_funcs
class TestDataExtractionFuncs:
    def test_get_ases(self, mock_caida_collector: CaidaCollector, decoded_path: Path):
        """Tests that _get_ases returns correctly from example file"""

        with decoded_path.open(mode="r") as f:
            lines = tuple([x.strip() for x in f.readlines()])
        (cp_links, peer_links, ixps, input_clique) = mock_caida_collector._get_ases(
            lines
        )

        ground_truth_cp_links = set(
            [
                CPLink(provider_asn=1, customer_asn=1898),
                CPLink(provider_asn=1, customer_asn=5401),
                CPLink(provider_asn=1, customer_asn=28618),
                CPLink(provider_asn=1, customer_asn=50017),
                CPLink(provider_asn=1, customer_asn=58243),
                CPLink(provider_asn=1, customer_asn=60664),
                CPLink(provider_asn=1, customer_asn=61396),
                CPLink(provider_asn=2, customer_asn=55855),
                CPLink(provider_asn=4, customer_asn=7633),
                CPLink(provider_asn=5, customer_asn=21710),
                CPLink(provider_asn=6, customer_asn=64031),
                CPLink(provider_asn=10, customer_asn=131401),
            ]
        )
        assert cp_links == ground_truth_cp_links
        ground_truth_peers = set(
            [
                PeerLink(1, 8641),
                PeerLink(1, 11537),
                PeerLink(1, 56847),
                PeerLink(1, 263036),
                PeerLink(1, 267701),
                PeerLink(2, 203427),
                PeerLink(2, 267222),
                PeerLink(3, 293),
                PeerLink(3, 6939),
                PeerLink(9, 35104),
            ]
        )
        assert peer_links == ground_truth_peers
        ground_truth_ixps = set(
            [
                1200,
                4635,
                5507,
                6695,
                7606,
                8714,
                9355,
                9439,
                9560,
                9722,
                9989,
                11670,
                15645,
                17819,
                18398,
                21371,
                24029,
                24115,
                24990,
                35054,
                40633,
                42476,
                43100,
                47886,
                48850,
                50384,
                55818,
                57463,
            ]
        )

        ground_truth_input_clique = set(
            [
                174,
                209,
                286,
                701,
                1239,
                1299,
                2828,
                2914,
                3257,
                3320,
                3356,
                3491,
                5511,
                6453,
                6461,
                6762,
                6830,
                7018,
                12956,
            ]
        )
        assert ixps == ground_truth_ixps
        ground_truth_input_clique = set(
            [
                174,
                209,
                286,
                701,
                1239,
                1299,
                2828,
                2914,
                3257,
                3320,
                3356,
                3491,
                5511,
                6453,
                6461,
                6762,
                6830,
                7018,
                12956,
            ]
        )

        assert input_clique == ground_truth_input_clique

    def test_extract_input_clique(self, mock_caida_collector: CaidaCollector):
        """Tests input_clique is decoded correctly"""

        line = (
            "# input clique: 174 209 286 701 1239 1299 2828 "
            "2914 3257 3320 3356 3491 5511 6453 6461 6762 "
            "6830 7018 12956"
        )
        ground_truth_input_clique = set(
            [
                174,
                209,
                286,
                701,
                1239,
                1299,
                2828,
                2914,
                3257,
                3320,
                3356,
                3491,
                5511,
                6453,
                6461,
                6762,
                6830,
                7018,
                12956,
            ]
        )
        test_input_clique: set[int] = set()
        # This is from the test bz2 file
        mock_caida_collector._extract_input_clique(line, test_input_clique)
        assert ground_truth_input_clique == test_input_clique

    def test_extract_ixp_ases(self, mock_caida_collector: CaidaCollector):
        """Tests ixps are decoded correctly"""

        line = (
            "# IXP ASes: 1200 4635 5507 6695 7606 8714 9355 9439 "
            "9560 9722 9989 11670 15645 17819 18398 21371 24029 "
            "24115 24990 35054 40633 42476 43100 47886 48850 "
            "50384 55818 57463"
        )
        ground_truth_ixps = set(
            [
                1200,
                4635,
                5507,
                6695,
                7606,
                8714,
                9355,
                9439,
                9560,
                9722,
                9989,
                11670,
                15645,
                17819,
                18398,
                21371,
                24029,
                24115,
                24990,
                35054,
                40633,
                42476,
                43100,
                47886,
                48850,
                50384,
                55818,
                57463,
            ]
        )
        test_ixps: set[int] = set()
        # This is from the test bz2 file
        mock_caida_collector._extract_ixp_ases(line, test_ixps)
        assert ground_truth_ixps == test_ixps

    def test_extract_provider_customers(self, mock_caida_collector: CaidaCollector):
        """Tests that provider customers are extracted correctly"""

        line = "1|1898|-1|bgp"
        test_cp_links: set[CPLink] = set()
        ground_truth_cp_links = set([CPLink(provider_asn=1, customer_asn=1898)])

        # This is from the test bz2 file
        mock_caida_collector._extract_provider_customers(line, test_cp_links)
        assert ground_truth_cp_links == test_cp_links

    def test_extract_peers(self, mock_caida_collector: CaidaCollector):
        """Tests that peers are extracted correctly"""

        line = "1|8641|0|bgp"
        test_peers: set[PeerLink] = set()
        ground_truth_peers = set([PeerLink(1, 8641)])

        # This is from the test bz2 file
        mock_caida_collector._extract_peers(line, test_peers)
        assert ground_truth_peers == test_peers
