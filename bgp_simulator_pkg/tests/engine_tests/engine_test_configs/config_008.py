from bgp_simulator_pkg.tests.engine_tests.graphs import graph_003
from bgp_simulator_pkg.tests.engine_tests.utils import EngineTestConfig

from bgp_simulator_pkg.simulation_engine import ROVAS, BGPAS
from bgp_simulator_pkg.enums import ASNs
from bgp_simulator_pkg.simulation_framework import ScenarioConfig, SubprefixHijack


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
    graph=graph_003,
)
