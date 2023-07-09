from bgpy.caida_collector import CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgpy.enums import ASNs


r"""
Modified version of Graph004, with new ASes 9 and 10,
with 10 being a provider of AS 4. This makes AS 4 multihomed.
"""

graph_035 = GraphInfo(
    customer_provider_links=set(
        [
            CPLink(provider_asn=1, customer_asn=4),
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=1, customer_asn=5),
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=4, customer_asn=6),
            CPLink(provider_asn=6, customer_asn=7),
            CPLink(provider_asn=6, customer_asn=8),
            CPLink(provider_asn=2, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=6),
            CPLink(provider_asn=5, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=9, customer_asn=5),
            CPLink(provider_asn=9, customer_asn=10),
            CPLink(provider_asn=10, customer_asn=4),
        ]
    )
)
