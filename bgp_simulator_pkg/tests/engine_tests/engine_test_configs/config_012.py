from bgp_simulator_pkg.tests.engine_tests.graphs import graph_006
from bgp_simulator_pkg.tests.engine_tests.utils import EngineTestConfig

from bgp_simulator_pkg.simulation_engine import BGPSimpleAS, ROVAS
from bgp_simulator_pkg.enums import ASNs
from bgp_simulator_pkg.simulation_framework import ScenarioConfig, NonRoutedPrefixHijack


config_012 = EngineTestConfig(
    name="012",
    desc="NonRouted Prefix Hijack",
    scenario_config=ScenarioConfig(
        ScenarioCls=NonRoutedPrefixHijack,
        AdoptASCls=ROVAS,
        BaseASCls=BGPSimpleAS,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict={2: ROVAS},
    ),
    graph=graph_006,
)
