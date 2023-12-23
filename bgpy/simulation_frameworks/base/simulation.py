from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from bgpy.as_graphs.base import ASGraphConstructor

    from bgpy.enums import SpecialPercentAdoptions

    from bgpy.simulation_frameworks.py_simulation_framework import GraphFactory
    from bgpy.simulation_frameworks.py_simulation_framework import MetricTracker
    from bgpy.simulation_frameworks.py_simulation_framework import ScenarioConfig

    from bgpy.simulation_engines.base import SimulationEngine

    from .as_graph_analyzer import ASGraphAnalyzer


class Simulation(ABC):
    """Runs simulations for BGP attack/defend scenarios"""

    @abstractmethod
    def __init__(
        self,
        percent_adoptions: tuple[Union[float, "SpecialPercentAdoptions"], ...],
        scenario_configs: tuple["ScenarioConfig", ...],
        num_trials: int,
        propagation_rounds: int,
        output_dir: Path,
        parse_cpus: int,
        python_hash_seed: Optional[int],
        ASGraphConstructorCls: type["ASGraphConstructor"],
        as_graph_constructor_kwargs,
        SimulationEngineCls: type["SimulationEngine"],
        ASGraphAnalyzerCls: type["ASGraphAnalyzer"],
        MetricTrackerCls: type["MetricTracker"],
    ) -> None:
        """Downloads relationship data, runs simulation"""

        raise NotImplementedError

    @abstractmethod
    def run(
        self,
        GraphFactoryCls: type["GraphFactory"],
        graph_factory_kwargs=None,
    ) -> None:
        """Runs the simulation and write the data"""

        raise NotImplementedError
