from ..victim_success_subgraph import VictimSuccessSubgraph
from .....enums import ASGroups
from .....enums import Outcomes


class VictimSuccessNonAdoptingStubsAndMHSubgraph(VictimSuccessSubgraph):
    """Graph for attacker success with non adopting stubs or multihomed ASes"""

    name: str = "victim_success_non_adopting_stubs_and_multihomed"

    def _get_subgraph_key(self, scenario, *args) -> str:  # type: ignore
        """Returns the key to be used in shared_data on the subgraph"""

        return self._get_as_type_pol_outcome_perc_k(
            ASGroups.STUBS_OR_MH,
            scenario.scenario_config.BaseASCls,
            Outcomes.VICTIM_SUCCESS,
        )
