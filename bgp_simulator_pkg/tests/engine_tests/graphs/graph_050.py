from caida_collector_pkg import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ....enums import ASNs


class Graph050(GraphInfo):
    r"""
    Image of scenario @ this link
    TODO: add link here
    """

    def __init__(self):
        super(Graph050, self).__init__(
            peer_links=set([PeerLink(1, 4)]),
            customer_provider_links=set(
                [
                    CPLink(provider_asn=2, customer_asn=4),
                    CPLink(provider_asn=2, customer_asn=5),
                    CPLink(provider_asn=4, customer_asn=6),
                    CPLink(provider_asn=4, customer_asn=8),
                    CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
                    CPLink(provider_asn=1, customer_asn=3),
                    CPLink(provider_asn=3, customer_asn=2),
                ]
            ),
        )
