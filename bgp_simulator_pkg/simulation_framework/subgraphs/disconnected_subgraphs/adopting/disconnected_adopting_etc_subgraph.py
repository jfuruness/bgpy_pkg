from ..disconnected_subgraph import AttackerSuccessSubgraph
from .....enums import ASTypes
from .....enums import Outcomes
from ....scenarios import Scenario


class AttackerSuccessAdoptingEtcSubgraph(AttackerSuccessSubgraph):
    """A graph for attacker success for etc ASes that adopt"""

    name: str = "disconnected_adopting_etc"

    def _get_subgraph_key(self,
                          scenario: Scenario,
                          *args) -> str:  # type: ignore
        """Returns the key to be used in shared_data on the subgraph"""

        return self._get_as_type_pol_outcome_perc_k(
            ASTypes.ETC, scenario.AdoptASCls, Outcomes.DISCONNECTED)

    @property
    def y_axis_label(self) -> str:
        """returns y axis label"""

        return Outcomes.DISCONNECTED.name
