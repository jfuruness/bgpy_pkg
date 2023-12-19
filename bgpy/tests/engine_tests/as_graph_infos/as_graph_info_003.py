from bgpy.as_graphs.base import CustomerProviderLink as CPLink

from bgpy.as_graphs.base import ASGraphInfo
from bgpy.enums import ASNs


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

as_graph_info_003 = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=1, customer_asn=4),
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=3, customer_asn=7),
            CPLink(provider_asn=4, customer_asn=8),
            CPLink(provider_asn=2, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=5),
            CPLink(provider_asn=5, customer_asn=ASNs.VICTIM.value),
        ]
    )
)
