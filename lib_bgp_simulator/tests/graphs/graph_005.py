from pathlib import Path

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from ...enums import ASNs


class Graph005(GraphInfo):
    r"""v3 example with ROV++v2

          /1\\
        2 |  \attacker_asn
       /   |   \
      /    | 3 \
     4    |/  \ \
      \    5   victim_asn
       \  /
        6
    """

    def __init__(self):
        super(Graph005, self).__init__(
            customer_provider_links=set(
                [CPLink(provider_asn=1, customer_asn=2),
                 CPLink(provider_asn=1, customer_asn=5),
                 CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
                 CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
                 CPLink(provider_asn=2, customer_asn=4),
                 CPLink(provider_asn=4, customer_asn=6),
                 CPLink(provider_asn=5, customer_asn=6),
                 CPLink(provider_asn=3, customer_asn=5),
                 CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value)]))
