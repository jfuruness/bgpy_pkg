from dataclasses import replace
from typing import TYPE_CHECKING
from warnings import warn

from bgpy.shared.exceptions import AnnouncementNotFoundError
from bgpy.simulation_engine.ann_containers import RIBsIn, RIBsOut, SendQueue
from bgpy.simulation_engine.policies.bgp import BGP

from .process_incoming_funcs import (
    _new_ann_better,
    _process_incoming_withdrawal,
    _select_best_ribs_in,
    _withdraw_ann_from_neighbors,
    process_incoming_anns,
)
from .propagate_funcs import _prev_sent, _process_outgoing_ann, _propagate, _send_anns
from .validation_funcs import (
    only_one_withdrawal_per_prefix_per_neighbor,
    only_one_ann_per_prefix_per_neighbor,
    no_implicit_withdrawals,
    not_withdrawing_new_ann,
    withdrawal_in_ribs_in,
    best_ann_isnt_the_withdrawn_ann,
)

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann


class BGPFull(BGP):
    name = "BGP Full"

    # Can't do this for backwards compatability reasons
    # error_on_invalid_routes: bool = False
    @property
    def error_on_invalid_routes(self) -> bool:
        """If True, anytime something invalid, error out, otherwise ignore

        This is for things like if you get two withdrawals for the same ann.
        This is an option because in some projects an attacker maliciously
        suppresses withdrawals so we don't want to error when this happens
        since it is intentional and not an oversight
        """

        return True

    def __init__(
        self,
        *args,
        ribs_in: RIBsIn | None = None,
        ribs_out: RIBsOut | None = None,
        send_q: SendQueue | None = None,
        **kwargs,
    ):
        super(BGPFull, self).__init__(*args, **kwargs)
        self.ribs_in: RIBsIn = ribs_in if ribs_in else RIBsIn()
        self.ribs_out: RIBsOut = ribs_out if ribs_out else RIBsOut()

    @property
    def _ribs_in(self) -> RIBsIn:
        warn(
            "Please use .ribs_in instead of ._ribs_in. "
            "This will be removed in a later version",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.ribs_in

    @property
    def _ribs_out(self) -> RIBsOut:
        warn(
            "Please use .ribs_out instead of ._ribs_out. "
            "This will be removed in a later version",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.ribs_out

    # Propagation functions
    _propagate = _propagate
    _process_outgoing_ann = _process_outgoing_ann
    _prev_sent = _prev_sent
    _send_anns = _send_anns

    # Process incoming funcs
    process_incoming_anns = process_incoming_anns
    _new_ann_better = _new_ann_better
    _process_incoming_withdrawal = _process_incoming_withdrawal
    _withdraw_ann_from_neighbors = _withdraw_ann_from_neighbors
    _select_best_ribs_in = _select_best_ribs_in

    # Validation funcs
    only_one_withdrawal_per_prefix_per_neighbor = only_one_withdrawal_per_prefix_per_neighbor
    only_one_ann_per_prefix_per_neighbor = only_one_ann_per_prefix_per_neighbor
    no_implicit_withdrawals = no_implicit_withdrawals
    not_withdrawing_new_ann = not_withdrawing_new_ann
    withdrawal_in_ribs_in = withdrawal_in_ribs_in
    best_ann_isnt_the_withdrawn_ann = best_ann_isnt_the_withdrawn_ann

    # NOTE: not sure why this is coded in such a weird fashion...
    def receive_ann(self, ann: "Ann", accept_withdrawals: bool = True) -> None:
        BGP.receive_ann(self, ann, accept_withdrawals=True)

    def prep_withdrawal_for_next_propagation(self, prefix: str) -> None:
        """Removes a prefix from the local RIB and withdraws it next propagation"""

        warn(
            "Now that I've refactored the withdrawals "
            "prep_withdrawal_for_next_propagation no longer "
            "makes sense and is deprecated since it doesn't deal with RIBsIn "
            "even though the name deceptively implies that it does. Please use: "
            " withdraw_ann = self.local_rib.pop(prefix).copy({'withdraw': True}); "
            "self.withdraw_ann_from_neighbors(withdraw_ann); "
            "This will be removed in a later version",
            category=DeprecationWarning,
            stacklevel=2,
        )

        # Create withdraw ann and remove the og from local rib
        withdraw_ann = self.local_rib.pop(prefix).copy({"withdraw": True})
        self.withdraw_ann_from_neighbors(withdraw_ann)

    def __to_yaml_dict__(self):
        """This optional method is called when you call yaml.dump()"""

        as_dict = super(BGPFull, self).__to_yaml_dict__()
        as_dict.update(
            {
                "ribs_in": self.ribs_in,
                "ribs_out": self.ribs_out,
            }
        )
        return as_dict
