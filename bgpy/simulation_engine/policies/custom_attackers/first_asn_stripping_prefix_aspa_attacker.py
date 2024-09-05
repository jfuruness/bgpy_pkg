from typing import TYPE_CHECKING

import bgpy
from bgpy.shared.enums import Relationships
from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_framework import Scenario


class FirstASNStrippingPrefixASPAAttacker(BGP):
    """Shortest path ASPA attacker uses origin hijacks to customers with ASPA

    This is meant to be used with the FirstASNStrippingPrefixHijack, but for ASPA, to
    customers the FirstASNStrippingPrefix is a forged-origin hijack (and we strip the
    first ASN from the path)
    """

    def process_incoming_anns(
        self,
        *,
        from_rel: "Relationships",
        propagation_round: int,
        scenario: "Scenario",
        reset_q: bool = True,
    ) -> None:
        """Asserts that we are using the FirstASNStrippingPrefixHijack, calls super"""

        err = "This is only meant for subclasses of FirstASNStrippingPrefixHijack"
        # Must... avoid... circular... imports!!
        ScenarioCls = bgpy.simulation_framework.scenarios.custom_scenarios.post_rov.first_asn_stripping_prefix_hijack.FirstASNStrippingPrefixHijack  # noqa:E501
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

        # If as path length is 1 (like it would be against BGP), don't modify it
        if (
            propagate_to == Relationships.CUSTOMERS
            and ann.recv_relationship == Relationships.ORIGIN
            and len(ann.as_path) > 1
        ):
            # Only need origin hijack when sending to customers,
            # but we also strip attacker's ASN
            new_ann = ann.copy({"as_path": (ann.origin), "seed_asn": None})
            self._process_outgoing_ann(neighbor, new_ann, propagate_to, send_rels)
            return True
        else:
            return False
