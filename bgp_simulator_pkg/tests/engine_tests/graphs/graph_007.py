from caida_collector_pkg import CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ....enums import ASNs


class Graph007(GraphInfo):
    r"""
              1
             / \
            2  3
              /  \
    attacker_asn  victim_asn
    """

    def __init__(self):
        super(Graph007, self).__init__(
            customer_provider_links=set(
                [CPLink(provider_asn=1, customer_asn=2),
                 CPLink(provider_asn=1, customer_asn=3),
                 CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
                 CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value)]))
