from ..graphs import Graph002
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
    ),
    graph=Graph002(),
)
