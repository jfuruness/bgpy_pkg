from ..disconnected_subgraph import AttackerSuccessSubgraph
from .....enums import ASTypes
from .....enums import Outcomes


class AttackerSuccessNonAdoptingInputCliqueSubgraph(AttackerSuccessSubgraph):
    """Graph with attacker success for non adopting input clique ASes"""

    name: str = "disconnected_non_adopting_input_clique_subgraph"

    def _get_subgraph_key(self, scenario, *args) -> str:  # type: ignore
        """Returns the key to be used in shared_data on the subgraph"""

        return self._get_as_type_pol_outcome_perc_k(ASTypes.INPUT_CLIQUE,
                                                    scenario.BaseASCls,
                                                    Outcomes.DISCONNECTED)

    @property
    def y_axis_label(self) -> str:
        """returns y axis label"""

        return Outcomes.DISCONNECTED.name
