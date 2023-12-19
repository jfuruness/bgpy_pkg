from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink

from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs


as_graph_info_020 = ASGraphInfo(
    peer_links=frozenset([]),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=32, customer_asn=12),
            CPLink(provider_asn=11, customer_asn=32),
            CPLink(provider_asn=11, customer_asn=77),
            CPLink(provider_asn=77, customer_asn=44),
            CPLink(provider_asn=44, customer_asn=33),
            CPLink(provider_asn=44, customer_asn=96),
            CPLink(provider_asn=44, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=44, customer_asn=55),
            CPLink(provider_asn=96, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=55, customer_asn=88),
            CPLink(provider_asn=88, customer_asn=89),
        ]
    ),
)
