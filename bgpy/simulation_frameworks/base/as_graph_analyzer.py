from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bgpy.simulation_engines.base import SimulationEngine
    from bgpy.simulation_framework.scenarios import Scenario


class ASGraphAnalyzer(ABC):
    """Takes in a SimulationEngine and outputs metrics"""

    @abstractmethod
    def __init__(
        self,
        engine: "SimulationEngine",
        scenario: "Scenario",
        data_plane_tracking: bool = True,
        control_plane_tracking: bool = False,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def analyze(self) -> dict[int, dict[int, int]]:
        """Takes in engine and outputs traceback for ctrl + data plane data"""

        raise NotImplementedError
