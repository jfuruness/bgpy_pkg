from typing import TYPE_CHECKING, Any, Optional
from warnings import warn

from bgpy.simulation_engine.ann_containers import LocalRIB, RecvQueue
from bgpy.simulation_engine.policies.policy import Policy

# Propagation functionality
from .propagate_funcs import (
    _policy_propagate,
    _prev_sent,
    _process_outgoing_ann,
    _propagate,
    propagate_to_customers,
    propagate_to_peers,
    propagate_to_providers,
)

if TYPE_CHECKING:
    from weakref import CallableProxyType

    from bgpy.as_graphs import AS
from typing import TYPE_CHECKING, Any

from bgpy.simulation_engine.ann_containers import RecvQueue

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcements import Announcement as Ann
    from bgpy.simulation_framework import Scenario

    from .bgp import BGP



from roa_checker import ROAChecker, ROAOutcome, ROARouted, ROAValidity

class BGP:
    name: str = "BGP"
    # from roa_checker import ROAChecker, ROAOutcome, ROARouted, ROAValidity
    roa_checker = ROAChecker()

    __slots__ = ("local_rib", "recv_q", "as_")

    def __init__(
        self,
        local_rib: LocalRIB | None = None,
        recv_q: RecvQueue | None = None,
        as_: Optional["AS"] = None,
    ) -> None:
        """Add local rib and data structures here

        This way they can be easily cleared later without having to redo
        the graph

        This is also useful for regenerating an AS from YAML
        """

        self.local_rib = local_rib if local_rib else LocalRIB()
        self.recv_q = recv_q if recv_q else RecvQueue()
        # This gets set within the AS class so it's fine
        self.as_: CallableProxyType[AS] = as_  # type: ignore

    # Propagation functionality
    propagate_to_providers = propagate_to_providers
    propagate_to_customers = propagate_to_customers
    propagate_to_peers = propagate_to_peers
    _propagate = _propagate
    _policy_propagate = _policy_propagate
    _process_outgoing_ann = _process_outgoing_ann

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[Any, Any]:
        """This optional method is called when you call yaml.dump()"""

        return {"local_rib": self.local_rib, "recv_q": self.recv_q}

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag) -> Policy:
        """This optional method is called when you call yaml.load()"""

        return cls(**dct)


    def seed_ann(self: "BGP", ann: "Ann") -> None:
        """Seeds an announcement at this AS

        Useful hook function used in BGPSec
        and later hopefully in the API for ROAs
        """

        # Ensure we aren't replacing anything
        err = f"Seeding conflict {ann} {self.local_rib.get(ann.prefix)}"
        assert self.local_rib.get(ann.prefix) is None, err
        # Seed by placing in the local rib
        self.local_rib.add_ann(ann)


    def receive_ann(self: "BGP", ann: "Ann", accept_withdrawals: bool = False) -> None:
        """Function for recieving announcements, adds to recv_q"""

        if getattr(ann, "withdraw", False) and not accept_withdrawals:
            raise NotImplementedError(f"Policy can't handle withdrawals {self.name}")
        self.recv_q.add_ann(ann)


    def process_incoming_anns(
        self: "BGP",
        *,
        from_rel: "Relationships",
        propagation_round: int,
        scenario: "Scenario",
        reset_q: bool = True,
    ) -> None:
        """Process all announcements that were incoming from a specific rel"""

        # For each prefix, get all anns recieved
        for prefix, ann_list in self.recv_q.items():
            # We already have ann from a prior rel that is better
            if self.local_rib.get(prefix) or not ann_list:
                continue
            else:
                for i, ann in enumerate(ann_list):
                    if self._valid_ann(ann, from_rel):
                        best_ann = ann
                        for j in range(i + 1, len(ann_list)):
                            ann = ann_list[i]
                            # NOTE: IF WE SORT PROP RANKS, TIEBREAKERS ARE AUTOMATIC!!! Since bigger or smaller AS always goes first
                            if self._valid_ann(ann, from_rel) and len(best_ann.as_path) > len(ann.as_path):
                                best_ann = ann
                        new_ann_processed = self._copy_and_process(best_ann, from_rel)
                        self.local_rib.add_ann(best_ann)
                        break

        self.recv_q = RecvQueue()


    def _valid_ann(
        self: "BGP",
        ann: "Ann",
        recv_relationship: "Relationships",
    ) -> bool:
        """Determine if an announcement is valid or should be dropped"""

        # Make sure there are no loops before propagating
        return True
        # BGP Loop Prevention Check
        # Newly added October 31 2024 - no AS 0 either
        self_asn = self.as_.asn
        for asn in ann.as_path:
            if asn == self_asn or asn == 0:
                return False
        return True


    def _copy_and_process(
        self: "BGP",
        ann: "Ann",
        recv_relationship: "Relationships",
        # overwrite_default_kwargs: dict[Any, Any] | None = None,
    ) -> "Ann":
        """Deep copies ann and modifies attrs

        Prepends AS to AS Path and sets recv_relationship
        """

        return ann.__class__(
            prefix=ann.prefix,
            as_path=(self.as_.asn, *ann.as_path),
            next_hop_asn=ann.next_hop_asn,
            seed_asn=None,
            recv_relationship=recv_relationship,
        )
        kwargs: dict[str, Any] = {
            "as_path": (self.as_.asn, *ann.as_path),
            "recv_relationship": recv_relationship,
            "seed_asn": None,
        }

        if overwrite_default_kwargs:
            kwargs.update(overwrite_default_kwargs)
        # Don't use a dict comp here for speed
        return ann.copy(overwrite_default_kwargs=kwargs)


    #############
    # ROA Funcs #
    #############

    def get_roa_outcome(self, ann: "Ann"):
        return self.roa_checker.get_roa_outcome_w_prefix_str_cached(
            ann.prefix, ann.origin
        )

    def ann_is_invalid_by_roa(self, ann: "Ann") -> bool:
        """Returns True if Ann is invalid by ROA

        False means ann is either valid or unknown
        """

        roa_outcome = self.roa_checker.get_roa_outcome_w_prefix_str_cached(
            ann.prefix, ann.origin
        )
        return ROAValidity.is_invalid(roa_outcome.validity)

    def ann_is_valid_by_roa(self, ann: "Ann") -> bool:
        """Returns True if Ann is valid by ROA

        False means ann is either invalid or unknown
        """

        roa_outcome = self.roa_checker.get_roa_outcome_w_prefix_str_cached(
            ann.prefix, ann.origin
        )
        return ROAValidity.is_valid(roa_outcome.validity)

    def ann_is_unknown_by_roa(self, ann: "Ann") -> bool:
        """Returns True if ann is not covered by roa"""

        roa_outcome = self.roa_checker.get_roa_outcome_w_prefix_str_cached(
            ann.prefix, ann.origin
        )
        return ROAValidity.is_unknown(roa_outcome.validity)

    def ann_is_covered_by_roa(self, ann: "Ann") -> bool:
        """Returns if an announcement has a roa"""

        return not self.ann_is_unknown_by_roa(ann)

    def ann_is_roa_non_routed(self, ann: "Ann") -> bool:
        """Returns bool for if announcement is routed according to ROA

        Need if statements in this fashion since there are three levels:
        valid invalid and unknown

        so not invalid != valid
        """

        if self.ann_is_invalid_by_roa(ann):
            relevant_roas = self.roa_checker.get_relevant_roas(ip_network(ann.prefix))
            return any(
                roa.routed_status == ROARouted.NON_ROUTED for roa in relevant_roas
            )
        return False

