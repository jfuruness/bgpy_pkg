from bgpy.caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgpy.enums import ASNs


graph_038 = GraphInfo(
    peer_links=set(
        [
            PeerLink(135, ASNs.VICTIM.value),
            PeerLink(7, 8),
            PeerLink(34, ASNs.ATTACKER.value),
            PeerLink(12, 34),
            PeerLink(11, 33),
        ]
    ),
    customer_provider_links=set(
        [
            CPLink(provider_asn=ASNs.VICTIM.value, customer_asn=34),
            CPLink(provider_asn=135, customer_asn=34),
            CPLink(provider_asn=135, customer_asn=12),
            CPLink(provider_asn=12, customer_asn=11),
            CPLink(provider_asn=34, customer_asn=33),
            CPLink(provider_asn=11, customer_asn=1),
            CPLink(provider_asn=33, customer_asn=1),
            CPLink(provider_asn=1, customer_asn=6),
            CPLink(provider_asn=6, customer_asn=7),
            CPLink(provider_asn=6, customer_asn=8),
        ]
    ),
)
