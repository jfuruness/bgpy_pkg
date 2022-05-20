from lib_caida_collector import CustomerProviderLink as CPLink
from lib_caida_collector import PeerLink


from .graph_info import GraphInfo
from ...enums import ASNs


class Graph044(GraphInfo):
    r"""
    Image of scenario @ this link
    TODO: add link here
    """

    def __init__(self):
        super(Graph044, self).__init__(
            peer_links=set([
                PeerLink(4, 3)
            ]),
            customer_provider_links=set(
                [
                    CPLink(provider_asn=1, customer_asn=4),
                    CPLink(provider_asn=5, customer_asn=ASNs.VICTIM.value),
                    CPLink(provider_asn=4, customer_asn=5),
                    CPLink(provider_asn=3, customer_asn=2),
                    CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
                    CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
                    CPLink(provider_asn=1, customer_asn=4),
                    CPLink(provider_asn=7, customer_asn=3),
                    CPLink(provider_asn=7, customer_asn=8)
                ]
            ),
        )
