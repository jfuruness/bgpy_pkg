from typing import TYPE_CHECKING

from bgpy.enums import Relationships
from bgpy.simulation_engine import BGP
from bgpy.simulation_framework.scenarios.custom_scenarios.post_rov.shortest_path_hijack import (
    ShortestPathHijack,
)


if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_framework import Scenario
    from bgpy.as_graphs import AS


class ShortestPathASPAAttacker(BGP):
    """Shortest path ASPA attacker uses origin hijacks to customers with ASPA

    This is meant to be used with the ShortestPathHijack, but for ASPA, to
    customers the ShortestPath is a forged-origin hijack
    """

    def process_incoming_anns(
        self,
        *,
        from_rel: "Relationships",
        propagation_round: int,
        scenario: "Scenario",
        reset_q: bool = True,
    ) -> None:
        """Asserts that we are using the ShortestPathHijack, then calls super"""

        err = "This class is only meant for subclasses of ShortestPathHijack"
        assert isinstance(scenario, ShortestPathHijack), err
        return super().process_incoming_anns(
            from_rel=from_rel,
            propagation_round=propagation_round,
            scenario=scenario,
            reset_q=reset_q,
        )

    def _policy_propagate(  # type: ignore
        self: "BGP",
        neighbor: "AS",
        ann: "Ann",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> bool:
        """As defined in ASPA V16 RFC section 12, use origin hijack for customers"""

        # This ann is originating from here, the attacker, so it's an attacker's ann
        if ann.from_rel == Relationships.ORIGIN:
            # Only need origin hijack when sending to customers
            new_ann = ann.copy({"as_path": (self.as_.asn, ann.origin)})
            self._process_outgoing_ann(neighbor, new_ann, propagate_to, send_rels)
            return True
        else:
            return False
