from ..attacker_success_subgraph import AttackerSuccessSubgraph
from .....enums import ASGroups
from .....enums import Outcomes
from bgpy.simulation_framework.scenarios import Scenario


class AttackerSuccessAdoptingEtcSubgraph(AttackerSuccessSubgraph):
    """A graph for attacker success for etc ASes that adopt"""

    name: str = "attacker_success_adopting_etc"

    def _get_subgraph_key(self, scenario: Scenario, *args) -> str:  # type: ignore
        """Returns the key to be used in shared_data on the subgraph"""

        return self._get_as_type_pol_outcome_perc_k(
            ASGroups.ETC, scenario.scenario_config.AdoptASCls, Outcomes.ATTACKER_SUCCESS
        )
