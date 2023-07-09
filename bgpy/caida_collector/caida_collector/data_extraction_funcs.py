from bgpy.caida_collector.links import CustomerProviderLink as CPLink
from bgpy.caida_collector.links import PeerLink


def _get_ases(
    self, lines: tuple[str, ...]
) -> tuple[set[CPLink], set[PeerLink], set[int], set[int]]:
    """Fills the initial AS dict and adds the following info:

    Creates AS dict with peers, providers, customers, input clique, ixps
    """

    input_clique: set[int] = set()
    ixps: set[int] = set()
    # Customer provider links
    cp_links: set[CPLink] = set()
    # Peer links
    peer_links: set[PeerLink] = set()
    for line in lines:
        # Get Caida input clique. See paper on site for what this is
        if line.startswith("# input clique"):
            self._extract_input_clique(line, input_clique)
        # Get detected Caida IXPs. See paper on site for what this is
        elif line.startswith("# IXP ASes"):
            self._extract_ixp_ases(line, ixps)
        # Not a comment, must be a relationship
        elif not line.startswith("#"):
            # Extract all customer provider pairs
            if "-1" in line:
                self._extract_provider_customers(line, cp_links)
            # Extract all peers
            else:
                self._extract_peers(line, peer_links)
    return cp_links, peer_links, ixps, input_clique


def _extract_input_clique(self, line: str, input_clique: set[int]):
    """Adds all ASNs within input clique line to ases dict"""

    # Gets all input ASes for clique
    for asn in line.split(":")[-1].strip().split(" "):
        # Insert AS into graph
        input_clique.add(int(asn))


def _extract_ixp_ases(self, line: str, ixps: set[int]):
    """Adds all ASNs that are detected IXPs to ASes dict"""

    # Get all IXPs that Caida lists
    for asn in line.split(":")[-1].strip().split(" "):
        ixps.add(int(asn))


def _extract_provider_customers(self, line: str, cp_links: set[CPLink]):
    """Extracts provider customers: <provider-as>|<customer-as>|-1"""

    provider_asn, customer_asn, _, source = line.split("|")
    cp_links.add(CPLink(customer_asn=int(customer_asn), provider_asn=int(provider_asn)))


def _extract_peers(self, line: str, peer_links: set[PeerLink]):
    """Extracts peers: <peer-as>|<peer-as>|0|<source>"""

    peer1_asn, peer2_asn, _, source = line.split("|")
    peer_links.add(PeerLink(int(peer1_asn), int(peer2_asn)))
