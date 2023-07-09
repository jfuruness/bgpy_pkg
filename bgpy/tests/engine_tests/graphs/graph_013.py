from bgpy.caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgpy.enums import ASNs


graph_013 = GraphInfo(
    peer_links=set(
        [
            PeerLink(1, 2),
            PeerLink(2, 4),
            PeerLink(4, 3),
            PeerLink(3, 1),
            PeerLink(2, 3),
            PeerLink(1, 4),
            PeerLink(5, 2),
            PeerLink(6, 7),
            PeerLink(8, 9),
            PeerLink(9, 10),
        ]
    ),
    customer_provider_links=set(
        [
            CPLink(provider_asn=5, customer_asn=6),
            CPLink(provider_asn=6, customer_asn=8),
            CPLink(provider_asn=6, customer_asn=9),
            CPLink(provider_asn=2, customer_asn=6),
            CPLink(provider_asn=2, customer_asn=7),
            CPLink(provider_asn=7, customer_asn=9),
            CPLink(provider_asn=7, customer_asn=10),
            CPLink(provider_asn=7, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=10, customer_asn=ASNs.VICTIM.value),
        ]
    ),
)
