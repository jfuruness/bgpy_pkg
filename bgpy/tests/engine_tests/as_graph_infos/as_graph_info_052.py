from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink, PeerLink

from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs

r"""

This graph can highlight every example of Gao Rexford Valley Free Routing

AS 666 announces subprefix
AS 777 announces prefix

(see config 035 for description)
      7   8
    / | \ |
   4--5--6
 / \  |  |
3  2  3  |
\  /   \ |
 666    777
"""


as_graph_info_052 = ASGraphInfo(
    peer_links=frozenset(
        {
            PeerLink(5, 8),
            PeerLink(8, 9),
            PeerLink(8, 3),
        }
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=5, customer_asn=1),
            CPLink(provider_asn=5, customer_asn=2),
            CPLink(provider_asn=8, customer_asn=4),
            CPLink(provider_asn=9, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=10, customer_asn=5),
            CPLink(provider_asn=10, customer_asn=8),
            CPLink(provider_asn=10, customer_asn=9),
            CPLink(provider_asn=11, customer_asn=9),
        ]
    ),
    diagram_ranks=(
        (ASNs.ATTACKER.value, ASNs.VICTIM.value),
        (1, 2, 3, 4),
        (5, 8, 9),
        (10, 11),
    ),
)
