from dataclasses import dataclass
from typing import Type

from ..graphs import GraphInfo
from ....simulation_framework import ScenarioConfig
from ....simulation_framework import Subgraph


@dataclass(frozen=True)
class EngineTestConfig:
    """Configuration info for the test suite"""

    name: str
    desc: str
    scenario_config: ScenarioConfig
    graph: GraphInfo
    propagation_rounds: int = 1
    SubgraphCls: Type[Subgraph] = Subgraph
