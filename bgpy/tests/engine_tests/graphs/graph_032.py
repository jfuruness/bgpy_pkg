from bgpy.caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgpy.enums import ASNs


graph_032 = GraphInfo(
    peer_links=set([PeerLink(3, 4)]),
    customer_provider_links=set(
        [
            CPLink(provider_asn=15, customer_asn=10),
            CPLink(provider_asn=15, customer_asn=16),
            CPLink(provider_asn=19, customer_asn=16),
            CPLink(provider_asn=16, customer_asn=17),
            CPLink(provider_asn=16, customer_asn=18),
            CPLink(provider_asn=17, customer_asn=6),
            CPLink(provider_asn=10, customer_asn=3),
            CPLink(provider_asn=10, customer_asn=6),
            CPLink(provider_asn=4, customer_asn=13),
            CPLink(provider_asn=3, customer_asn=1),
            CPLink(provider_asn=3, customer_asn=2),
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=5),
            CPLink(provider_asn=5, customer_asn=11),
            CPLink(provider_asn=5, customer_asn=12),
            CPLink(provider_asn=5, customer_asn=6),
            CPLink(provider_asn=12, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=6, customer_asn=7),
            CPLink(provider_asn=6, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=7, customer_asn=8),
            CPLink(provider_asn=7, customer_asn=9),
            CPLink(provider_asn=13, customer_asn=14),
            CPLink(provider_asn=14, customer_asn=6),
        ]
    ),
)
