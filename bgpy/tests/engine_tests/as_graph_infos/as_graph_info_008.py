from bgpy.as_graphs import PeerLink, CustomerProviderLink as CPLink

from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs


r"""
          1 --- 2
         / \    \
        3  4     5
          /  \
attacker_asn  victim_asn
"""

as_graph_info_008 = ASGraphInfo(
    peer_links=frozenset([PeerLink(1, 2)]),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=1, customer_asn=4),
            CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=5),
        ]
    ),
)
