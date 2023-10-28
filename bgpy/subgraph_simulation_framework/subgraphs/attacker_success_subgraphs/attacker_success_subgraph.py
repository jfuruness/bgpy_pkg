from abc import abstractmethod
from typing import TYPE_CHECKING

from ..subgraph import Subgraph


if TYPE_CHECKING:
    from bgpy.simulation_framework.scenarios import Scenario


class AttackerSuccessSubgraph(Subgraph):
    """A subgraph for data display"""

    @abstractmethod
    def _get_subgraph_key(self, scenario: "Scenario", *args) -> str:
        """Returns the key to be used in shared_data on the subgraph"""

        raise NotImplementedError

    @property
    def y_axis_label(self) -> str:
        """returns y axis label"""

        return "Data Plane % Hijacked"
