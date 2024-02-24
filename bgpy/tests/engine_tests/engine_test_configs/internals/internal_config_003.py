from frozendict import frozendict
from bgpy.tests.engine_tests.utils import EngineTestConfig


from bgpy.simulation_engine import BGP, OnlyToCustomers
from bgpy.simulation_framework import (
    AccidentalRouteLeak,
    ScenarioConfig,
)
from bgpy.enums import ASNs

from bgpy.as_graphs import PeerLink
from bgpy.as_graphs import ASGraphInfo


r"""Graph to test OTC from a peer

777 - 666 - 1
"""

as_graph_info = ASGraphInfo(
    peer_links=frozenset(
        [
            PeerLink(ASNs.VICTIM.value, ASNs.ATTACKER.value),
            PeerLink(ASNs.ATTACKER.value, 1),
        ]
    ),
    customer_provider_links=frozenset(),
)


internal_config_003 = EngineTestConfig(
    name="internal_003",
    desc="Accidental route leak to a peer with OTC Simple",
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        BasePolicyCls=BGP,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                1: OnlyToCustomers,
                ASNs.VICTIM.value: OnlyToCustomers,
            }
        ),
    ),
    as_graph_info=as_graph_info,
)
