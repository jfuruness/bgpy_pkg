from frozendict import frozendict
from bgpy.tests.engine_tests.graphs import graph_001
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGPAS
from bgpy.enums import ASNs
from bgpy.simulation_framework import ScenarioConfig, SubprefixHijack


config_002 = EngineTestConfig(
    name="002",
    desc="BGP hidden hijack",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BaseASCls=BGPAS,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    graph=graph_001,
)