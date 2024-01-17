from bgpy.as_graphs import PeerLink, CustomerProviderLink as CPLink

from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs


r"""Hidden hijack example with BGP
Figure 1a in our ROV++ paper

    1
     \
     2 - 3
    /     \
   777     666
"""

as_graph_info_001 = ASGraphInfo(
    peer_links=frozenset([PeerLink(2, 3)]),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
        ]
    ),
)
