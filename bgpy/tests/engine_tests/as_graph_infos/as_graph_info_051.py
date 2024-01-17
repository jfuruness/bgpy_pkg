from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink

from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs


as_graph_info_051 = ASGraphInfo(
    peer_links=frozenset(),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=9, customer_asn=10),
            CPLink(provider_asn=9, customer_asn=5),
            CPLink(provider_asn=10, customer_asn=4),
            CPLink(provider_asn=1, customer_asn=5),
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=1, customer_asn=4),
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=2, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=6),
            CPLink(provider_asn=6, customer_asn=7),
            CPLink(provider_asn=6, customer_asn=8),
            CPLink(provider_asn=4, customer_asn=6),
        ]
    ),
)
