from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ....enums import ASNs


class Graph008(GraphInfo):
    r"""
              1 --- 2
             / \    \
            3  4     5
              /  \
    attacker_asn  victim_asn
    """

    def __init__(self):
        super(Graph008, self).__init__(
            peer_links=set([PeerLink(1, 2)]),
            customer_provider_links=set(
                [CPLink(provider_asn=1, customer_asn=3),
                 CPLink(provider_asn=1, customer_asn=4),
                 CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
                 CPLink(provider_asn=4, customer_asn=ASNs.ATTACKER.value),
                 CPLink(provider_asn=2, customer_asn=5)]))
