from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import BGP
from bgpy.simulation_framework import PrefixHijack, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

r"""Graph to test that a pure-peer node (no PC links) is placed correctly.

Before the diagram row-assignment fix, node 3 (which has only a peer link to
node 2 and no provider-customer links) was stranded at row 0 alongside the
leaves because propagation_rank_funcs assigned it rank 0.  The fix computes
diagram rows via longest-path-from-root, which correctly places node 3 at the
same row as node 2.

        1
       / \
      2   ATTACKER
      |
    VICTIM
      |
      3 (pure peer of 2, no PC links)
"""

as_graph_info = ASGraphInfo(
    peer_links=frozenset(
        [
            PeerLink(2, 3),
        ]
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
        ]
    ),
)


internal_config_008 = EngineTestConfig(
    name="internal_008",
    desc="Pure-peer node with no PC links (tests diagram row placement fix)",
    scenario_config=ScenarioConfig(
        ScenarioCls=PrefixHijack,
        BasePolicyCls=BGP,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        hardcoded_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info,
)
