from ..graphs import graph_002
from ..utils import EngineTestConfig

from ....simulation_engine import ROVSimpleAS
from ....enums import ASNs
from ....simulation_framework import ScenarioConfig, ValidPrefix


config_005 = EngineTestConfig(
    name="005",
    desc="Basic BGP Propagation (with ROV Simple AS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=ROVSimpleAS,
        override_victim_asns={ASNs.VICTIM.value},
        override_non_default_asn_cls_dict=dict(),
    ),
    graph=graph_002,
)
