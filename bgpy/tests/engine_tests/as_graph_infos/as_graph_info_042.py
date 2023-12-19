from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink


from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs


as_graph_info_042 = ASGraphInfo(
    peer_links=frozenset([]),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=32, customer_asn=25),
            CPLink(provider_asn=77, customer_asn=32),
            CPLink(provider_asn=77, customer_asn=44),
            CPLink(provider_asn=44, customer_asn=33),
            CPLink(provider_asn=44, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=44, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=15, customer_asn=32),
            CPLink(provider_asn=15, customer_asn=14),
            CPLink(provider_asn=14, customer_asn=13),
            CPLink(provider_asn=13, customer_asn=12),
            CPLink(provider_asn=12, customer_asn=11),
            CPLink(provider_asn=11, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=24, customer_asn=25),
            CPLink(provider_asn=24, customer_asn=23),
            CPLink(provider_asn=23, customer_asn=22),
            CPLink(provider_asn=22, customer_asn=21),
            CPLink(provider_asn=21, customer_asn=ASNs.VICTIM.value),
        ]
    ),
)
