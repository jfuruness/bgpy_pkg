from bgpy.caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgpy.enums import ASNs


graph_012 = GraphInfo(
    peer_links=set([PeerLink(4, 5), PeerLink(3, 7), PeerLink(7, 6)]),
    customer_provider_links=set(
        [
            CPLink(provider_asn=11, customer_asn=2),
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=3, customer_asn=2),
            CPLink(provider_asn=4, customer_asn=3),
            CPLink(provider_asn=7, customer_asn=8),
            CPLink(provider_asn=8, customer_asn=9),
            CPLink(provider_asn=9, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=11, customer_asn=10),
            CPLink(provider_asn=10, customer_asn=5),
            CPLink(provider_asn=5, customer_asn=6),
            CPLink(provider_asn=6, customer_asn=ASNs.ATTACKER.value),
        ]
    ),
)
