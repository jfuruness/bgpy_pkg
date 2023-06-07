from ..graphs import Graph003
from ..utils import EngineTestConfig

from ....simulation_engine import ROVSimpleAS, BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import ScenarioConfig, SubprefixHijack


config_007 = EngineTestConfig(
    name="007",
    desc="Fig 2 (ROVSimpleAS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BaseASCls=BGPSimpleAS,
        override_attacker_asns={ASNs.ATTACKER.value},
        override_victim_asns={ASNs.VICTIM.value},
        AdoptASCls=ROVSimpleAS,
        override_non_default_asn_cls_dict={3: ROVSimpleAS, 4: ROVSimpleAS},
    ),
    graph=Graph003(),
)
