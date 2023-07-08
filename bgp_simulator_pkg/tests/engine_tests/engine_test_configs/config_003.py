from bgp_simulator_pkg.tests.engine_tests.graphs import graph_002
from bgp_simulator_pkg.tests.engine_tests.utils import EngineTestConfig

from bgp_simulator_pkg.simulation_engine import BGPSimpleAS
from bgp_simulator_pkg.enums import ASNs
from bgp_simulator_pkg.simulation_framework import ScenarioConfig, ValidPrefix


config_003 = EngineTestConfig(
    name="003",
    desc="Basic BGP Propagation (with simple AS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=BGPSimpleAS,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=dict(),
    ),
    graph=graph_002,
)
