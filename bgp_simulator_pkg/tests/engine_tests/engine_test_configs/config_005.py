from frozendict import frozendict
from bgp_simulator_pkg.tests.engine_tests.graphs import graph_002
from bgp_simulator_pkg.tests.engine_tests.utils import EngineTestConfig

from bgp_simulator_pkg.simulation_engine import ROVSimpleAS
from bgp_simulator_pkg.enums import ASNs
from bgp_simulator_pkg.simulation_framework import ScenarioConfig, ValidPrefix


config_005 = EngineTestConfig(
    name="005",
    desc="Basic BGP Propagation (with ROV Simple AS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=ROVSimpleAS,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    graph=graph_002,
)
