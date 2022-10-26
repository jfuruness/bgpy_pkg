from ..disconnected_subgraph import AttackerSuccessSubgraph
from .....enums import ASTypes
from .....enums import Outcomes


class AttackerSuccessNonAdoptingStubsAndMHSubgraph(AttackerSuccessSubgraph):
    """Graph for attacker success with non adopting stubs or multihomed ASes"""

    name: str = "disconnected_non_adopting_stubs_and_multihomed"

    def _get_subgraph_key(self, scenario, *args) -> str:  # type: ignore
        """Returns the key to be used in shared_data on the subgraph"""

        return self._get_as_type_pol_outcome_perc_k(
            ASTypes.STUBS_OR_MH, scenario.BaseASCls, Outcomes.DISCONNECTED)

    @property
    def y_axis_label(self) -> str:
        """returns y axis label"""

        return Outcomes.DISCONNECTED.name
