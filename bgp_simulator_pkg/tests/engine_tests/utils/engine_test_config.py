from caida_collector_pkg import AS
from dataclasses import dataclass, field
from typing import Dict, Optional, Type

from ....simulation_framework import Graph
from ....simulation_framework import Scenario
from ....simulation_framework import Subgraph


@dataclass(frozen=True)
class EngineTestConfig:
    """Configuration info for the test suite"""

    name: str
    desc: str
    scenario: Scenario
    graph: Graph
    propagation_rounds: int = 1
    SubgraphCls: Type[Subgraph] = Subgraph
