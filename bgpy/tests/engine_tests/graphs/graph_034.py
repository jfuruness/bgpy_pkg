from bgpy.caida_collector import CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgpy.enums import ASNs


r"""
Modified example of Graph034 with an additional peer link connection
between AS 1 and 4.
"""

graph_034 = GraphInfo(
    customer_provider_links=set(
        [
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=4, customer_asn=1),
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=3, customer_asn=7),
            CPLink(provider_asn=4, customer_asn=8),
            CPLink(provider_asn=4, customer_asn=6),
            CPLink(provider_asn=2, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=5),
            CPLink(provider_asn=5, customer_asn=ASNs.VICTIM.value),
        ]
    )
)
