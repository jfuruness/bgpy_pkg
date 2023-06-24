from dataclasses import dataclass

from bgp_simulator_pkg.tests.engine_tests.graphs import GraphInfo
from bgp_simulator_pkg.simulation_framework import ScenarioConfig
from bgp_simulator_pkg.simulation_framework import Subgraph


@dataclass(frozen=True, slots=True)
class EngineTestConfig:
    """Configuration info for the test suite"""

    name: str
    desc: str
    scenario_config: ScenarioConfig
    graph: GraphInfo
    propagation_rounds: int = 1
    SubgraphCls: type[Subgraph] = Subgraph
