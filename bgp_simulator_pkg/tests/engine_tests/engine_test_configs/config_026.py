from frozendict import frozendict
from bgp_simulator_pkg.tests.engine_tests.graphs import graph_019
from bgp_simulator_pkg.tests.engine_tests.utils import EngineTestConfig

from bgp_simulator_pkg.simulation_engine import ROVAS
from bgp_simulator_pkg.enums import ASNs
from bgp_simulator_pkg.simulation_framework import ScenarioConfig, ValidPrefix


config_026 = EngineTestConfig(
    name="026",
    desc="Test of tiebreak preference",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=ROVAS,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    graph=graph_019,
)
