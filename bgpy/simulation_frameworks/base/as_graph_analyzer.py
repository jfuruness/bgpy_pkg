from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from bgpy.enums import CPPOutcomes, PyOutcomes
    from bgpy.simulation_engines.base import SimulationEngine
    from bgpy.simulation_framework.scenarios import Scenario


class ASGraphAnalyzer(ABC):
    """Takes in a SimulationEngine and outputs metrics"""

    @abstractmethod
    def __init__(self, engine: "SimulationEngine", scenario: "Scenario") -> None:
        raise NotImplementedError

    @abstractmethod
    def analyze(self) -> dict[int, dict[int, Union["CPPOutcomes", "PyOutcomes"]]]:
        """Takes in engine and outputs traceback for ctrl + data plane data"""

        raise NotImplementedError
