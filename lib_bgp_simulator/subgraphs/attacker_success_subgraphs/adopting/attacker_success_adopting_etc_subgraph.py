from ..attacker_success_subgraph import AttackerSuccessSubgraph
from ....enums import ASTypes
from ....enums import Outcomes


class AttackerSuccessAdoptingEtcSubgraph(AttackerSuccessSubgraph):
    """A graph for attacker success for etc ASes that adopt"""

    name = "attacker_success_adopting_etc"

    def _get_subgraph_key(self, scenario, *args):
        """Returns the key to be used in shared_data on the subgraph"""

        return self._get_as_type_pol_outcome_perc_k(
            ASTypes.ETC, scenario.AdoptASCls, Outcomes.ATTACKER_SUCCESS)
