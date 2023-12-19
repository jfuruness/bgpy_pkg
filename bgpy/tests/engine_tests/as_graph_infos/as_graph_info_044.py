from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink


from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs


as_graph_info_044 = ASGraphInfo(
    peer_links=frozenset([PeerLink(4, 3)]),
    customer_provider_links=frozenset(
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
