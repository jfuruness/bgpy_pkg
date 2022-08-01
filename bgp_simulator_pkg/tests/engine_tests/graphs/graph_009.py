from caida_collector_pkg import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ....enums import ASNs


class Graph009(GraphInfo):
    r"""
    This is the v1 vs v2 graph
    It has ASNs.ATTACKER.value ASes.
    """

    def __init__(self):
        super(Graph009, self).__init__(
            peer_links=set([
                PeerLink(1, 2),
                PeerLink(3, 2),
                PeerLink(2, 4),
                PeerLink(2, 5)
            ]),
            customer_provider_links=set([
                CPLink(provider_asn=6, customer_asn=2),
                CPLink(provider_asn=6, customer_asn=4),
                CPLink(provider_asn=1, customer_asn=7),
                CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=3, customer_asn=9),
                CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=9, customer_asn=ASNs.ATTACKER.value)
            ])
        )
