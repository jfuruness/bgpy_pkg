from caida_collector_pkg import CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ....enums import ASNs


class Graph006(GraphInfo):
    r"""
            1
           / \
          2   attacker_asn
         /
        3
    """

    def __init__(self):
        super(Graph006, self).__init__(
            customer_provider_links=set(
                [CPLink(provider_asn=1, customer_asn=2),
                 CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
                 CPLink(provider_asn=2, customer_asn=3)]))
