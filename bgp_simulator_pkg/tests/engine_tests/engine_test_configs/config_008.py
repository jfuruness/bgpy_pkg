from typing import Dict, Type

from caida_collector_pkg import AS

from ..graphs import Graph003
from ..utils import EngineTestConfig

from ....simulation_engine import ROVAS, BGPAS
from ....enums import ASNs
from ....simulation_framework import ScenarioConfig, SubprefixHijack


config_008 = EngineTestConfig(
    name="008",
    desc="Fig 2 (ROVSimpleAS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        AdoptASCls=ROVAS,
        BaseASCls=BGPAS,
        override_attacker_asns={ASNs.ATTACKER.value},
        override_victim_asns={ASNs.VICTIM.value},
        override_non_default_asn_cls_dict={3: ROVAS, 4: ROVAS},
    ),
    graph=Graph003(),
)
