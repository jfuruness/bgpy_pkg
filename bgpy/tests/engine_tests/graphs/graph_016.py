from bgpy.caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgpy.enums import ASNs


graph_016 = GraphInfo(
    peer_links=set(
        [
            PeerLink(1, 2),
            PeerLink(2, 4),
            PeerLink(4, 3),
            PeerLink(3, 1),
            PeerLink(2, 3),
            PeerLink(1, 4),
            PeerLink(5, 2),
            PeerLink(5, 11),
            PeerLink(13, 12),
            PeerLink(12, 6),
            PeerLink(6, 7),
            PeerLink(14, 8),
            PeerLink(8, 9),
            PeerLink(9, 10),
        ]
    ),
    customer_provider_links=set(
        [
            CPLink(provider_asn=11, customer_asn=12),
            CPLink(provider_asn=11, customer_asn=13),
            CPLink(provider_asn=5, customer_asn=6),
            CPLink(provider_asn=5, customer_asn=12),
            CPLink(provider_asn=2, customer_asn=12),
            CPLink(provider_asn=2, customer_asn=6),
            CPLink(provider_asn=2, customer_asn=7),
            CPLink(provider_asn=13, customer_asn=14),
            CPLink(provider_asn=12, customer_asn=14),
            CPLink(provider_asn=6, customer_asn=8),
            CPLink(provider_asn=6, customer_asn=9),
            CPLink(provider_asn=7, customer_asn=9),
            CPLink(provider_asn=7, customer_asn=10),
            CPLink(provider_asn=14, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=14, customer_asn=21),
            CPLink(provider_asn=14, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=14, customer_asn=19),
            CPLink(provider_asn=8, customer_asn=19),
            CPLink(provider_asn=9, customer_asn=19),
            CPLink(provider_asn=9, customer_asn=18),
            CPLink(provider_asn=9, customer_asn=16),
            CPLink(provider_asn=9, customer_asn=15),
            CPLink(provider_asn=10, customer_asn=17),
            CPLink(provider_asn=10, customer_asn=15),
            CPLink(provider_asn=100, customer_asn=150),
        ]
    ),
)
