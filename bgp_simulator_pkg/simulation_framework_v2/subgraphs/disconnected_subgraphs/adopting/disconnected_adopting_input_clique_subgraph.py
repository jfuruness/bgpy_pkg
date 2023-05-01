from ..disconnected_subgraph import DisconnectedSubgraph
from .....enums import ASTypes
from .....enums import Outcomes
from ....scenarios import ScenarioTrial


class DisconnectedAdoptingInputCliqueSubgraph(DisconnectedSubgraph):
    """Graph with attacker success for adopting input clique ASes"""

    name: str = "disconnected_adopting_input_clique"

    def _get_subgraph_key(self,
                          scenario: ScenarioTrial,
                          *args) -> str:  # type: ignore
        """Returns the key to be used in shared_data on the subgraph"""

        return self._get_as_type_pol_outcome_perc_k(ASTypes.INPUT_CLIQUE,
                                                    scenario.scenario_config.AdoptASCls,
                                                    Outcomes.DISCONNECTED)
