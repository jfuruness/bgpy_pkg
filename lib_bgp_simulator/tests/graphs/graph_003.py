from pathlib import Path

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ...enums import ASNs


class Graph003(GraphInfo):
    r"""v1 example with ROV

           1\ \
          /| \ \
         / |  \ attacker_asn
        /  | 2 \
       3   | /\ \
      /    4   5 \
     7     |    \ \
           8     victim_asn
    """

    def __init__(self):
        super(Graph003, self).__init__(
            customer_provider_links=set(
                [CPLink(provider_asn=1, customer_asn=3),
                 CPLink(provider_asn=1, customer_asn=4),
                 CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
                 CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
                 CPLink(provider_asn=3, customer_asn=7),
                 CPLink(provider_asn=4, customer_asn=8),
                 CPLink(provider_asn=2, customer_asn=4),
                 CPLink(provider_asn=2, customer_asn=5),
                 CPLink(provider_asn=5, customer_asn=ASNs.VICTIM.value)]))
