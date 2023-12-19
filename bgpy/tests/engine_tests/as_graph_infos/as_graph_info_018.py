from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink

from bgpy.as_graphs import ASGraphInfo
from bgpy.enums import ASNs


r"""
Test path length preference in gao_rexford.py.

  1
 / \
|   3
2   |
|   4
 \ /
 777

"""

as_graph_info_018 = ASGraphInfo(
    peer_links=frozenset([]),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
        ]
    ),
)
