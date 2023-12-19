from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink

from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs


r"""
Modified version of Graph004, with new ASes 9 and 10,
with 10 being a provider of AS 4. This makes AS 4 multihomed.
"""

as_graph_info_036 = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=1, customer_asn=5),
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=4),
            CPLink(provider_asn=4, customer_asn=9),
            CPLink(provider_asn=4, customer_asn=10),
            CPLink(provider_asn=4, customer_asn=8),
            CPLink(provider_asn=9, customer_asn=13),
            CPLink(provider_asn=13, customer_asn=6),
            CPLink(provider_asn=10, customer_asn=111),
            CPLink(provider_asn=111, customer_asn=6),
            CPLink(provider_asn=111, customer_asn=15),
            CPLink(provider_asn=8, customer_asn=12),
            CPLink(provider_asn=12, customer_asn=14),
            CPLink(provider_asn=14, customer_asn=6),
            CPLink(provider_asn=14, customer_asn=15),
            CPLink(provider_asn=5, customer_asn=8),
            CPLink(provider_asn=3, customer_asn=5),
            CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
        ]
    )
)
