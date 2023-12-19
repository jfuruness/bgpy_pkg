from frozendict import frozendict
from bgpy.tests.engine_tests.graphs import as_graph_info_019
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGPPolicy
from bgpy.enums import ASNs
from bgpy.simulation_framework import ScenarioConfig, ValidPrefix


config_024 = EngineTestConfig(
    name="024",
    desc="Test of tiebreak preference",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=BGPPolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_as_graph_info_info=as_graph_info_019,
)
