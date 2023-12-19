from bgpy.as_graphs import PeerLink, CustomerProviderLink as CPLink

from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs


r"""
Modified example of Graph033 with an additional peer link connection
between AS 1 and 4.
"""

as_graph_info_048 = ASGraphInfo(
    peer_links=frozenset(
        [
            PeerLink(1, 4),
        ]
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=3, customer_asn=7),
            CPLink(provider_asn=4, customer_asn=8),
            CPLink(provider_asn=4, customer_asn=6),
            CPLink(provider_asn=2, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=5),
        ]
    ),
)
