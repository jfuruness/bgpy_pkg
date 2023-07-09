from bgpy.caida_collector import CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgpy.enums import ASNs


r"""
        1
       / \
      2   attacker_asn
     /
    3
"""

graph_006 = GraphInfo(
    customer_provider_links=set(
        [
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=3),
        ]
    )
)
