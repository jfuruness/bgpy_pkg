from ..graphs import Graph003
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import ScenarioConfig, SubprefixHijack


config_010 = EngineTestConfig(
    name="010",
    desc="Fig 2 (ROVSimpleAS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BaseASCls=BGPSimpleAS,
        override_attacker_asns={ASNs.ATTACKER.value},
        override_victim_asns={ASNs.VICTIM.value},
    ),
    graph=Graph003(),
)
