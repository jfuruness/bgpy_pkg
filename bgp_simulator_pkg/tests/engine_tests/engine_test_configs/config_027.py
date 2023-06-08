from ..graphs import Graph040
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....simulation_framework import ScenarioConfig, ValidPrefix


config_027 = EngineTestConfig(
    name="027",
    desc="Test of customer preference",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=BGPSimpleAS,
        num_victims=3,
        override_victim_asns={2, 3, 4},
        override_non_default_asn_cls_dict=dict()
    ),
    graph=Graph040(),
)
