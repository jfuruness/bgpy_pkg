from bgp_simulator_pkg.tests.engine_tests.graphs import graph_006
from bgp_simulator_pkg.tests.engine_tests.utils import EngineTestConfig

from bgp_simulator_pkg.simulation_engine import BGPSimpleAS, ROVSimpleAS
from bgp_simulator_pkg.enums import ASNs
from bgp_simulator_pkg.simulation_framework import (
    ScenarioConfig,
    NonRoutedSuperprefixHijack,
)


config_013 = EngineTestConfig(
    name="013",
    desc="NonRouted Superprefix Hijack",
    scenario_config=ScenarioConfig(
        ScenarioCls=NonRoutedSuperprefixHijack,
        AdoptASCls=ROVSimpleAS,
        BaseASCls=BGPSimpleAS,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict={2: ROVSimpleAS},
    ),
    graph=graph_006,
)
