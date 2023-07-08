from frozendict import frozendict
from bgp_simulator_pkg.tests.engine_tests.graphs import graph_001
from bgp_simulator_pkg.tests.engine_tests.utils import EngineTestConfig

from bgp_simulator_pkg.simulation_engine import BGPSimpleAS
from bgp_simulator_pkg.enums import ASNs
from bgp_simulator_pkg.simulation_framework import ScenarioConfig, SubprefixHijack


config_001 = EngineTestConfig(
    name="001",
    desc="BGP hidden hijack (with simple AS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BaseASCls=BGPSimpleAS,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    graph=graph_001,
)
