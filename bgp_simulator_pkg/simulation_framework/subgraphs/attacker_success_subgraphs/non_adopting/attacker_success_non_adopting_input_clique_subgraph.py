from ..attacker_success_subgraph import AttackerSuccessSubgraph
from .....enums import ASGroups
from .....enums import Outcomes


class AttackerSuccessNonAdoptingInputCliqueSubgraph(AttackerSuccessSubgraph):
    """Graph with attacker success for non adopting input clique ASes"""

    name: str = "attacker_success_non_adopting_input_clique_subgraph"

    def _get_subgraph_key(self, scenario, *args) -> str:  # type: ignore
        """Returns the key to be used in shared_data on the subgraph"""

        return self._get_as_type_pol_outcome_perc_k(
            ASGroups.INPUT_CLIQUE,
            scenario.scenario_config.BaseASCls,
            Outcomes.ATTACKER_SUCCESS,
        )
