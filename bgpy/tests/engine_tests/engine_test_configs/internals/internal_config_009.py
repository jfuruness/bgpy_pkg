from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import BGP
from bgpy.simulation_framework import PrefixHijack, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

r"""Graph to test the peer-triangle diagram placement fix.

Before the fix, a greedy peer-alignment pass would move node 10 (pure-peer
node with no PC links) from row 0 to align with node 4, then the next pair
(4, 66) would try to align node 4 with 66.  This broke the 10-4 alignment,
leaving 10 stranded.  In addition, peer edges drawn as directed edges without
constraint="false" created hidden Graphviz rank cycles that reversed arrows.

The fix uses _peer_move_safe, which refuses to move a node if another peer
is already sharing its current row, and adds constraint="false" to all peer
edges to prevent hidden rank constraints.

         4
        /|\
       1  3  ATTACKER
       |  |
      66 VICTIM
      (peers: 66-10, 10-4, 4-66  — a peer triangle)
      10 has no PC links
"""

as_graph_info = ASGraphInfo(
    peer_links=frozenset(
        [
            PeerLink(66, 10),
            PeerLink(10, 4),
            PeerLink(4, 66),
        ]
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=4, customer_asn=1),
            CPLink(provider_asn=4, customer_asn=3),
            CPLink(provider_asn=4, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=1, customer_asn=66),
        ]
    ),
)


internal_config_009 = EngineTestConfig(
    name="internal_009",
    desc="Peer triangle with floating node (tests peer de-alignment fix)",
    scenario_config=ScenarioConfig(
        ScenarioCls=PrefixHijack,
        BasePolicyCls=BGP,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        hardcoded_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info,
)
