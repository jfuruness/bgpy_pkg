from .victim_success_subgraph import VictimSuccessSubgraph
from ....enums import Outcomes
from bgpy.simulation_framework.scenarios import Scenario


class VictimSuccessAllSubgraph(VictimSuccessSubgraph):
    """A graph for attacker success for etc ASes that adopt"""

    name: str = "victim_success_all"

    def _get_subgraph_key(self, scenario: Scenario, *args) -> str:
        """Returns the key to be used in shared_data on the subgraph"""

        return f"all_{Outcomes.VICTIM_SUCCESS.name}_perc"
