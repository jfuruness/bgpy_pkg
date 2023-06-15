from ..graphs import graph_006
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS, ROVSimpleAS
from ....enums import ASNs
from ....simulation_framework import ScenarioConfig, NonRoutedSuperprefixHijack


config_013 = EngineTestConfig(
    name="013",
    desc="NonRouted Superprefix Hijack",
    scenario_config=ScenarioConfig(
        ScenarioCls=NonRoutedSuperprefixHijack,
        AdoptASCls=ROVSimpleAS,
        BaseASCls=BGPSimpleAS,
        override_attacker_asns={ASNs.ATTACKER.value},
        override_victim_asns={ASNs.VICTIM.value},
        override_non_default_asn_cls_dict={2: ROVSimpleAS},
    ),
    graph=graph_006,
)
