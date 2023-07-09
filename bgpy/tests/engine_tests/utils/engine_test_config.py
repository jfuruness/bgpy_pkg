from dataclasses import dataclass
from typing import ClassVar

from bgpy.tests.engine_tests.graphs import GraphInfo
from bgpy.simulation_framework.scenarios import ScenarioConfig
from bgpy.simulation_framework.metric_tracker.metric_tracker import (
    MetricTracker,
)
from bgpy.simulation_framework.graph_analyzer import GraphAnalyzer


@dataclass(frozen=True, slots=True)
class EngineTestConfig:
    """Configuration info for the test suite"""

    name: str
    desc: str
    scenario_config: ScenarioConfig
    graph: GraphInfo
    propagation_rounds: int = 1
    MetricTrackerCls: type[MetricTracker] = MetricTracker
    GraphAnalyzerCls: type[GraphAnalyzer] = GraphAnalyzer
    _used_names: ClassVar[set[str]] = set()

    def __post_init__(self):
        """Names are used as folder names for testing, can't have duplicates"""

        if self.name in EngineTestConfig._used_names:
            raise ValueError(f"The name '{self.name}' is already in use.")
        EngineTestConfig._used_names.add(self.name)
