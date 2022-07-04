from lib_caida_collector import CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ....enums import ASNs


class Graph018(GraphInfo):
    r"""
    Test path length preference in gao_rexford.py.

      1
     / \
    |   3
    2   |
    |   4
     \ /
     777

    """

    def __init__(self):
        super(Graph018, self).__init__(
            peer_links=set([]),
            customer_provider_links=set(
                [CPLink(provider_asn=1, customer_asn=2),
                 CPLink(provider_asn=1, customer_asn=3),
                 CPLink(provider_asn=3, customer_asn=4),
                 CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
                 CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
                 ]))
