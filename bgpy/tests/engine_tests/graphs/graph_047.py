from bgpy.caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo


r"""Graph to test relationship preference

      2
     /
    1 - 3
     \
      4
     /
    5
"""

graph_047 = GraphInfo(
    peer_links=set([PeerLink(1, 3)]),
    customer_provider_links=set(
        [
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=1, customer_asn=4),
            CPLink(provider_asn=4, customer_asn=5),
        ]
    ),
)
