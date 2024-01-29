from dataclasses import dataclass

from bgpy.as_graphs import ASGraphInfo, ASGraph, CAIDAASGraph
from bgpy.simulation_framework.scenarios import ScenarioConfig
from bgpy.simulation_engine import BaseSimulationEngine, SimulationEngine
from bgpy.simulation_framework.metric_tracker.metric_tracker import MetricTracker
from bgpy.simulation_framework.as_graph_analyzers import (
    BaseASGraphAnalyzer,
    ASGraphAnalyzer,
)
from bgpy.simulation_framework import AccidentalRouteLeak
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
    propagation_rounds: int = 1
    ASGraphCls: type[ASGraph] = CAIDAASGraph
    SimulationEngineCls: type[BaseSimulationEngine] = SimulationEngine  # type: ignore
    MetricTrackerCls: type[MetricTracker] = MetricTracker
    ASGraphAnalyzerCls: type[BaseASGraphAnalyzer] = ASGraphAnalyzer
    DiagramCls: type[Diagram] = Diagram

    def __post_init__(self):
        if (
            self.scenario_config.ScenarioCls == AccidentalRouteLeak
            and self.propagation_rounds < 2
        ):
            raise ValueError("propagation_rounds must be >= 2 for AccidentalRouteLeak")
