from ..graphs import graph_002
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import ScenarioConfig, ValidPrefix


config_003 = EngineTestConfig(
    name="003",
    desc="Basic BGP Propagation (with simple AS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=BGPSimpleAS,
        override_victim_asns={ASNs.VICTIM.value},
        override_non_default_asn_cls_dict=dict(),
    ),
    graph=graph_002,
)
