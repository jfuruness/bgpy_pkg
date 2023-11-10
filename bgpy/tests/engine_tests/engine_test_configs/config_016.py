from frozendict import frozendict
from bgpy.tests.engine_tests.graphs import graph_018
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGPPolicy
from bgpy.enums import ASNs
from bgpy.simulation_framework import ScenarioConfig, ValidPrefix


config_016 = EngineTestConfig(
    name="016",
    desc="Test of path length preference",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=BGPPolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    graph=graph_018,
)
