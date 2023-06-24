from bgp_simulator_pkg.caida_collector import CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgp_simulator_pkg.enums import ASNs


r"""
          1
         / \
        2  3
          /  \
attacker_asn  victim_asn
"""

graph_007 = GraphInfo(
    customer_provider_links=set(
        [
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
        ]
    )
)
