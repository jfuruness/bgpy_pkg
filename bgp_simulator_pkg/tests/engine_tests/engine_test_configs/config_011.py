from ..graphs import Graph006
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS, ROVSimpleAS
from ....enums import ASNs
from ....simulation_framework import ScenarioConfig, NonRoutedPrefixHijack


config_011 = EngineTestConfig(
    name="011",
    desc="NonRouted Prefix Hijack",
    scenario_config=ScenarioConfig(
        ScenarioCls=NonRoutedPrefixHijack,
        AdoptASCls=ROVSimpleAS,
        BaseASCls=BGPSimpleAS,
        override_attacker_asns={ASNs.ATTACKER.value},
        override_victim_asns={ASNs.VICTIM.value},
        override_non_default_asn_cls_dict={2: ROVSimpleAS},
    ),
    graph=Graph006(),
)
