from bgpy.as_graphs import PeerLink, CustomerProviderLink as CPLink

from bgpy.as_graphs import ASGraphInfo


r"""Graph to test relationship preference

      2
     /
    1 - 3
     \
      4
     /
    5
"""

as_graph_info_047 = ASGraphInfo(
    peer_links=frozenset([PeerLink(1, 3)]),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=1, customer_asn=4),
            CPLink(provider_asn=4, customer_asn=5),
        ]
    ),
)
