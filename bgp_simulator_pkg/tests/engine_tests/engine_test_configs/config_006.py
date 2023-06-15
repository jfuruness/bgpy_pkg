from ..graphs import graph_002
from ..utils import EngineTestConfig

from ....simulation_engine import ROVAS
from ....enums import ASNs
from ....simulation_framework import ScenarioConfig, ValidPrefix


config_006 = EngineTestConfig(
    name="006",
    desc="Basic BGP Propagation (with ROV AS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=ROVAS,
        override_victim_asns={ASNs.VICTIM.value},
        override_non_default_asn_cls_dict=dict(),
    ),
    graph=graph_002,
)
