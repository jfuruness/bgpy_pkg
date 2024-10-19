from typing import TYPE_CHECKING

from roa_checker import ROAValidity

from bgpy.shared.enums import Relationships
from bgpy.simulation_engine.policies.rovpp.v1.rovpp_v1_lite import ROVPPV1Lite

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine import Announcement as Ann


class ROVPPV2Lite(ROVPPV1Lite):
    """An Policy that deploys ROV++V2 Lite as defined in the ROV++ paper

    ROV++ Improved Deployable Defense against BGP Hijacking

    """

    name: str = "ROV++V2 Lite"

    def _policy_propagate(
        self,
        neighbor: "AS",
        ann: "Ann",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> bool:
        """Deals with blackhole propagation

        If ann is a blackhole, it must be recv from peers/providers and must
        be sent only to customers
        """

        # If blackhole and subprefix or non-routed
        if ann.rovpp_blackhole:
            if self._send_competing_hijack_allowed(ann, propagate_to):
                self._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)
            return True
        else:
            return False

    def _send_competing_hijack_allowed(
        self, ann: "Ann", propagate_to: Relationships
    ) -> bool:
        """You can send blackhole to customers if from peer/provider
        and either subprefix or non routed
        """
        return (
            # From peer/provider
            ann.recv_relationship
            in [Relationships.PEERS, Relationships.PROVIDERS, Relationships.ORIGIN]
            # Sending to customers
            and propagate_to == Relationships.CUSTOMERS
            # subprefix or non routed (don't send blackholes for prefixes)
            # To tell if it's a subprefix hijack we check if it's invalid by length
            and (
                self.get_roa_outcome(ann).validity
                not in (
                    ROAValidity.INVALID_LENGTH,
                    ROAValidity.INVALID_LENGTH_AND_ORIGIN,
                )
                or not self.ann_is_roa_non_routed(ann)
            )
        )
