from typing import TYPE_CHECKING

import bgpy
from bgpy.shared.enums import Relationships
from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_framework import Scenario


class ShortestPathPrefixASPAAttacker(BGP):
    """Shortest path ASPA attacker uses origin hijacks to customers with ASPA

    This is meant to be used with the ShortestPathPrefixHijack, but for ASPA, to
    customers the ShortestPathPrefix is a forged-origin hijack
    """

    def process_incoming_anns(
        self,
        *,
        from_rel: "Relationships",
        propagation_round: int,
        scenario: "Scenario",
        reset_q: bool = True,
    ) -> None:
        """Asserts that we are using the ShortestPathPrefixHijack, then calls super"""

        err = "This class is only meant for subclasses of ShortestPathPrefixHijack"
        # Must... avoid... circular... imports!!
        ScenarioCls = bgpy.simulation_framework.scenarios.custom_scenarios.post_rov.shortest_path_prefix_hijack.ShortestPathPrefixHijack  # noqa:E501
        assert isinstance(scenario, ScenarioCls), err
        return super().process_incoming_anns(
            from_rel=from_rel,
            propagation_round=propagation_round,
            scenario=scenario,
            reset_q=reset_q,
        )

    def _policy_propagate(
        self: "BGP",
        neighbor: "AS",
        ann: "Ann",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> bool:
        """As defined in ASPA V16 RFC section 12, use origin hijack for customers"""

        # This ann is originating from here, the attacker, so it's an attacker's ann
        # If as path length is 1 (like it would be against BGP), don't modify it
        if (
            propagate_to == Relationships.CUSTOMERS
            and ann.recv_relationship == Relationships.ORIGIN
            and len(ann.as_path) > 1
        ):
            # Only need origin hijack when sending to customers
            new_ann = ann.copy(
                {"as_path": (self.as_.asn, ann.origin), "seed_asn": None},
            )
            self._process_outgoing_ann(neighbor, new_ann, propagate_to, send_rels)
            return True
        else:
            return False
