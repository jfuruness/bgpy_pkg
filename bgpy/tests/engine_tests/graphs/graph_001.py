from bgpy.caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgpy.enums import ASNs


r"""Hidden hijack example with BGP
Figure 1a in our ROV++ paper

    1
     \
     2 - 3
    /     \
   777     666
"""

graph_001 = GraphInfo(
    peer_links=set([PeerLink(2, 3)]),
    customer_provider_links=set(
        [
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
        ]
    ),
)
