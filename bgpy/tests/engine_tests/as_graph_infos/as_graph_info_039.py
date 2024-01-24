from bgpy.as_graphs import PeerLink, CustomerProviderLink as CPLink

from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs


as_graph_info_039 = ASGraphInfo(
    peer_links=frozenset([PeerLink(56, 78), PeerLink(7, 8)]),
    customer_provider_links=frozenset(
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
