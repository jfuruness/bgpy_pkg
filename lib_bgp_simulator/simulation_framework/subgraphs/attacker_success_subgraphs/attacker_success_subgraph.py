from abc import abstractmethod
from ..subgraph import Subgraph


class AttackerSuccessSubgraph(Subgraph):
    """A subgraph for data display"""

    @abstractmethod
    def _get_subgraph_key(self, *args) -> str:
        """Returns the key to be used in shared_data on the subgraph"""

        raise NotImplementedError

    @property
    @abstractmethod
    def y_axis_label(self) -> str:
        """returns y axis label"""

        raise NotImplementedError
