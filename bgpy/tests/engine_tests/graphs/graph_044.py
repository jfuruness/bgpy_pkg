from bgpy.caida_collector import CustomerProviderLink as CPLink
from bgpy.caida_collector import PeerLink


from .graph_info import GraphInfo
from bgpy.enums import ASNs


graph_044 = GraphInfo(
    peer_links=set([PeerLink(4, 3)]),
    customer_provider_links=set(
        [
            CPLink(provider_asn=1, customer_asn=4),
            CPLink(provider_asn=5, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=5),
            CPLink(provider_asn=3, customer_asn=2),
            CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=1, customer_asn=4),
            CPLink(provider_asn=7, customer_asn=3),
            CPLink(provider_asn=7, customer_asn=8),
        ]
    ),
)
