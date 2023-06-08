from ..graphs import Graph040
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....simulation_framework import ScenarioConfig, ValidPrefix


config_028 = EngineTestConfig(
    name="028",
    desc="Test of peer preference",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=BGPSimpleAS,
        num_victims=2,
        override_victim_asns={2, 3},
        override_non_default_asn_cls_dict=dict()
    ),
    graph=Graph040(),
)
