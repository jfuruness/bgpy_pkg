from bgpy.caida_collector import CustomerProviderLink as CPLink, PeerLink

from .graph_info import GraphInfo
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


graph_052 = GraphInfo(
    peer_links=set({
        PeerLink(4, 5),
        PeerLink(5, 6)
    }),
    customer_provider_links=set(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=1),
            CPLink(provider_asn=4, customer_asn=2),
            CPLink(provider_asn=5, customer_asn=3),
            CPLink(provider_asn=6, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=7, customer_asn=4),
            CPLink(provider_asn=7, customer_asn=5),
            CPLink(provider_asn=7, customer_asn=6),
            CPLink(provider_asn=8, customer_asn=6),
        ]
    ),
    diagram_ranks=[
        [ASNs.ATTACKER.value, ASNs.VICTIM.value],
        [1, 2, 3],
        [4, 5, 6],
        [7, 8],
    ]
)
