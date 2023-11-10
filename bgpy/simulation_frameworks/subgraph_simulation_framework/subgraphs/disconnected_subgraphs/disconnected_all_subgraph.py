from .disconnected_subgraph import DisconnectedSubgraph
from ....enums import Outcomes
from bgpy.simulation_framework.scenarios import Scenario


class DisconnectedAllSubgraph(DisconnectedSubgraph):
    """A graph for attacker success for etc ASes that adopt"""

    name: str = "disconnected_all"

    def _get_subgraph_key(self, scenario: Scenario, *args) -> str:
        """Returns the key to be used in shared_data on the subgraph"""

        return f"all_{Outcomes.DISCONNECTED.name}_perc"
