from ..graphs import graph_017
from ..utils import EngineTestConfig

from ....simulation_engine import BGPAS
from ....enums import ASNs
from ....simulation_framework import ScenarioConfig, ValidPrefix


config_020 = EngineTestConfig(
    name="020",
    desc="Test of relationship preference",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=BGPAS,
        override_attacker_asns={ASNs.ATTACKER.value},
        override_victim_asns={ASNs.VICTIM.value},
        override_non_default_asn_cls_dict=dict(),
    ),
    graph=graph_017,
)
