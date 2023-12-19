from dataclasses import dataclass
from typing import ClassVar

from bgpy.as_graphs import ASGraphInfo, ASGraph, CAIDAASGraph
from bgpy.simulation_framework.scenarios import ScenarioConfig
from bgpy.simulation_engine import SimulationEngine
from bgpy.simulation_framework.metric_tracker.metric_tracker import (
    MetricTracker,
)
from bgpy.simulation_framework.graph_analyzer import GraphAnalyzer

from .diagram import Diagram


@dataclass(frozen=True, slots=True)
class EngineTestConfig:
    """Configuration info for the test suite"""

    name: str
    desc: str
    scenario_config: ScenarioConfig
    as_graph_info: ASGraphInfo
    propagation_rounds: int = 1
    ASGraphCls: type[ASGraph] = (CAIDAASGraph,)
    SimulationEngineCls: type[SimulationEngine] = SimulationEngine
    MetricTrackerCls: type[MetricTracker] = MetricTracker
    GraphAnalyzerCls: type[GraphAnalyzer] = GraphAnalyzer
    DiagramCls: type[Diagram] = Diagram
    _used_names: ClassVar[set[str]] = set()

    def __post_init__(self):
        """Names are used as folder names for testing, can't have duplicates"""

        if self.name in EngineTestConfig._used_names:
            raise ValueError(f"The name '{self.name}' is already in use.")
        EngineTestConfig._used_names.add(self.name)
