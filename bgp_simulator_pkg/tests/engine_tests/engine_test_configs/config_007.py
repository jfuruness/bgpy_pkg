from frozendict import frozendict
from bgp_simulator_pkg.tests.engine_tests.graphs import graph_003
from bgp_simulator_pkg.tests.engine_tests.utils import EngineTestConfig

from bgp_simulator_pkg.simulation_engine import ROVSimpleAS, BGPSimpleAS
from bgp_simulator_pkg.enums import ASNs
from bgp_simulator_pkg.simulation_framework import ScenarioConfig, SubprefixHijack


config_007 = EngineTestConfig(
    name="007",
    desc="Fig 2 (ROVSimpleAS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BaseASCls=BGPSimpleAS,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        AdoptASCls=ROVSimpleAS,
        override_non_default_asn_cls_dict=frozendict({3: ROVSimpleAS, 4: ROVSimpleAS}),
    ),
    graph=graph_003,
)
