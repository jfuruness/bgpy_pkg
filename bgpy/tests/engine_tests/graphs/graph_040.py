from bgpy.caida_collector import PeerLink, CustomerProviderLink as CPLink

from .graph_info import GraphInfo


r"""Graph to test relationship preference

      2
     /
5 - 1 - 3
     \
      4
"""

graph_040 = GraphInfo(
    peer_links=set([PeerLink(1, 3), PeerLink(1, 5)]),
    customer_provider_links=set(
        [
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=1, customer_asn=4),
        ]
    ),
)
