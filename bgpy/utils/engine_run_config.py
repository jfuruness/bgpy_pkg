from dataclasses import dataclass

from bgpy.as_graphs import ASGraphInfo, ASGraph, CAIDAASGraph
from bgpy.simulation_frameworks.py_simulation_framework.scenarios import ScenarioConfig
from bgpy.simulation_engines.base import SimulationEngine
from bgpy.simulation_engines.py_simulation_engine import PySimulationEngine
from bgpy.simulation_framework.py_simulation_frameworks.metric_tracker.metric_tracker import (
    MetricTracker,
)
from bgpy.simulation_frameworks.base.as_graph_analyzer import ASGraphAnalyzer
from bgpy.simulation_frameworks.py_simulation_framework.py_as_graph_analyzer import (
    PyASGraphAnalyzer,
)

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
    SimulationEngineCls: type[SimulationEngine] = PySimulationEngine
    MetricTrackerCls: type[MetricTracker] = MetricTracker
    GraphAnalyzerCls: type[ASGraphAnalyzer] = PyASGraphAnalyzer
    DiagramCls: type[Diagram] = Diagram
