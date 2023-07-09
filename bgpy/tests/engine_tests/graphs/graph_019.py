from bgpy.caida_collector import CustomerProviderLink as CPLink

from .graph_info import GraphInfo
from bgpy.enums import ASNs


r"""
Test tiebreak preference in gao_rexford.py.

  1
 / \
2   3
|   |
5   4
 \ /
 777

The lower ASN, 2, should be preferred by 1.
"""

graph_019 = GraphInfo(
    peer_links=set([]),
    customer_provider_links=set(
        [
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=5),
            CPLink(provider_asn=5, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
        ]
    ),
)
