from abc import abstractmethod
from typing import TYPE_CHECKING

from ..subgraph import Subgraph


if TYPE_CHECKING:
    from ...scenarios import ScenarioTrial


class DisconnectedSubgraph(Subgraph):
    """A subgraph for data display"""

    @abstractmethod
    def _get_subgraph_key(self, scenario: "ScenarioTrial", *args) -> str:
        """Returns the key to be used in shared_data on the subgraph"""

        raise NotImplementedError

    @property
    def y_axis_label(self) -> str:
        """returns y axis label"""

        return "Data Plane % Disconnected"
