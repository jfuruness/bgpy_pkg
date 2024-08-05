from typing import TYPE_CHECKING

from bgpy.enums import Relationships
from bgpy.simulation_engine.policies.bgp import BGP
import bgpy


if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_framework import Scenario
    from bgpy.as_graphs import AS


class FirstASNStrippingASPAAttacker(BGP):
    """Shortest path ASPA attacker uses origin hijacks to customers with ASPA

    This is meant to be used with the FirstASNStrippingHijack, but for ASPA, to
    customers the FirstASNStripping is a forged-origin hijack (and we strip the
    first ASN from the path)
    """

    # Mypy doesn't understand superclass since superclass is in a seperate file
    def process_incoming_anns(  # type: ignore
        self,
        *,
        from_rel: "Relationships",
        propagation_round: int,
        scenario: "Scenario",
        reset_q: bool = True,
    ) -> None:
        """Asserts that we are using the FirstASNStrippingHijack, then calls super"""

        err = "This class is only meant for subclasses of FirstASNStrippingHijack"
        # Must... avoid... circular... imports!!
        ScenarioCls = (
            bgpy.simulation_framework.scenarios.custom_scenarios.post_rov.first_asn_stripping_hijack.FirstASNStrippingHijack
        )
        assert isinstance(scenario, ScenarioCls), err
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
            # Only need origin hijack when sending to customers,
            # but we also strip attacker's ASN
            new_ann = ann.copy({"as_path": (ann.origin), "seed_asn": None})
            self._process_outgoing_ann(neighbor, new_ann, propagate_to, send_rels)
            return True
        else:
            return False
