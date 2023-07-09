from bgpy.caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgpy.enums import ASNs


graph_039 = GraphInfo(
    peer_links=set([PeerLink(56, 78), PeerLink(7, 8)]),
    customer_provider_links=set(
        [
            CPLink(provider_asn=56, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=56, customer_asn=33),
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=33, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=6),
            CPLink(provider_asn=6, customer_asn=7),
            CPLink(provider_asn=6, customer_asn=8),
            CPLink(provider_asn=78, customer_asn=ASNs.ATTACKER.value),
        ]
    ),
)
