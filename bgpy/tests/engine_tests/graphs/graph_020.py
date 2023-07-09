from bgpy.caida_collector import CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgpy.enums import ASNs


graph_020 = GraphInfo(
    peer_links=set([]),
    customer_provider_links=set(
        [
            CPLink(provider_asn=32, customer_asn=12),
            CPLink(provider_asn=11, customer_asn=32),
            CPLink(provider_asn=11, customer_asn=77),
            CPLink(provider_asn=77, customer_asn=44),
            CPLink(provider_asn=44, customer_asn=33),
            CPLink(provider_asn=44, customer_asn=96),
            CPLink(provider_asn=44, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=44, customer_asn=55),
            CPLink(provider_asn=96, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=55, customer_asn=88),
            CPLink(provider_asn=88, customer_asn=89),
        ]
    ),
)
