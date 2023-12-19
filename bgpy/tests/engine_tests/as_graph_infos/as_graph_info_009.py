from bgpy.as_graphs import PeerLink, CustomerProviderLink as CPLink

from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs


r"""
This is the v1 vs v2 graph
It has ASNs.ATTACKER.value ASes.
"""

as_graph_info_009 = ASGraphInfo(
    peer_links=frozenset(
        [PeerLink(1, 2), PeerLink(3, 2), PeerLink(2, 4), PeerLink(2, 5)]
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=6, customer_asn=2),
            CPLink(provider_asn=6, customer_asn=4),
            CPLink(provider_asn=1, customer_asn=7),
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=3, customer_asn=9),
            CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=9, customer_asn=ASNs.ATTACKER.value),
        ]
    ),
)
