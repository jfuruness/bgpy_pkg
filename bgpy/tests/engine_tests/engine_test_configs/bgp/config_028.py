from frozendict import frozendict
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_040
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGPSimplePolicy
from bgpy.simulation_framework import (
    ScenarioConfig,
    ValidPrefix,
)


config_028 = EngineTestConfig(
    name="028",
    desc="Test of peer preference",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=BGPSimplePolicy,
        num_victims=2,
        override_victim_asns=frozenset({2, 3}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_040,
)
