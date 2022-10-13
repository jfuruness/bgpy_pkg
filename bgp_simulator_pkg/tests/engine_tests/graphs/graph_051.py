from caida_collector_pkg import CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ....enums import ASNs


class Graph051(GraphInfo):
    r"""
    Image of scenario @ this link
    TODO: add link here
    """

    def __init__(self):
        super(Graph051, self).__init__(
            peer_links=set(),
            customer_provider_links=set(
                [
                    CPLink(provider_asn=9, customer_asn=10),
                    CPLink(provider_asn=9, customer_asn=5),
                    CPLink(provider_asn=10, customer_asn=4),
                    CPLink(provider_asn=1, customer_asn=5),
                    CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
                    CPLink(provider_asn=1, customer_asn=4),
                    CPLink(provider_asn=1, customer_asn=2),
                    CPLink(provider_asn=2, customer_asn=3),
                    CPLink(provider_asn=3, customer_asn=6),
                    CPLink(provider_asn=6, customer_asn=7),
                    CPLink(provider_asn=6, customer_asn=8),
                    CPLink(provider_asn=4, customer_asn=6)
                ]
            ),
        )
