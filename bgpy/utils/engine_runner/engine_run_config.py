from dataclasses import dataclass

from bgpy.as_graphs import ASGraph, ASGraphInfo, CAIDAASGraph
from bgpy.simulation_engine import BaseSimulationEngine, SimulationEngine
from bgpy.simulation_framework.as_graph_analyzers import (
    ASGraphAnalyzer,
    BaseASGraphAnalyzer,
)
from bgpy.simulation_framework.graph_data_aggregator.graph_data_aggregator import (
    GraphDataAggregator,
)
from bgpy.simulation_framework.scenarios import ScenarioConfig

from .diagram import Diagram


@dataclass(frozen=True, slots=True)
class EngineRunConfig:
    """Configuration info for a single engine run

    Useful for tests, API calls, or just running a single configuration
    """

    name: str
    desc: str
    scenario_config: ScenarioConfig
    as_graph_info: ASGraphInfo
    requires_provider_cones: bool = False
    ASGraphCls: type[ASGraph] = CAIDAASGraph
    # Only concrete classes are allowed, but not going to bother with a protocol here
    SimulationEngineCls: type[BaseSimulationEngine] = SimulationEngine  # type: ignore
    GraphDataAggregatorCls: type[GraphDataAggregator] = GraphDataAggregator
    ASGraphAnalyzerCls: type[BaseASGraphAnalyzer] = ASGraphAnalyzer
    DiagramCls: type[Diagram] = Diagram
