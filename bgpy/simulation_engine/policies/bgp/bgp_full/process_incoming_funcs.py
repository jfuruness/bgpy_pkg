from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.ann_containers import AnnInfo, SendInfo
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_framework import Scenario

    from .bgp_full import BGPFull


def process_incoming_anns(
    self: "BGPFull",
    *,
    from_rel: "Relationships",
    propagation_round: int,
    # Usually None for attack
    scenario: "Scenario",
    reset_q: bool = True,
):
    """Process all announcements that were incoming from a specific rel"""

    for prefix, ann_list in self.recv_q.items():
        # Get announcement currently in local rib
        current_ann: Ann | None = self.local_rib.get(prefix)
        og_ann = current_ann

        # For each announcement that is incoming
        for new_ann in ann_list:
            # Validation funcs
            assert self.assert_only_one_withdrawal_per_prefix_per_neighbor(ann_list)
            assert self.only_one_ann_per_prefix_per_neighbor(ann_list)

            # If withdrawal remove from RIBsIn, otherwise add to RIBsIn
            self._process_new_ann_in_ribs_in(new_ann, prefix, from_rel)

            # Process withdrawals even for invalid anns in the ribs_in
            if new_ann.withdraw:
                current_ann = self._withdraw_from_local_rib_and_get_new_best_ann(
                    og_ann, new_ann, current_ann
                )
            else:
                current_ann = self._get_new_best_ann(current_ann, new_ann, from_rel)

        if og_ann != current_ann:
            self.local_rib.add_ann(current_ann)
            self._withdraw_ann_from_neighbors(og_ann.copy({"withdraw": True})

    self._reset_q(reset_q)


def _process_new_ann_in_ribs_in(
    self, unprocessed_ann: "Ann", prefix: str, from_rel: Relationships
) -> bool:
    """Adds ann to ribs in if the ann is not a withdrawal"""

    # Remove ann using withdrawal from RIBsIn
    if ann.withdraw:
        neighbor = unprocessed_ann.as_path[0]
        # Remove ann from Ribs in
        self.ribs_in.remove_entry(neighbor, prefix, self.error_on_invalid_routes)
    # Add ann to RIBsIn
    else:
        assert self.no_implicit_withdrawals(unprocessed_ann, prefix)
        self.ribs_in.add_unprocessed_ann(unprocessed_ann, from_rel)


def _withdraw_from_local_rib_and_get_new_best_ann(
    og_ann: Ann, new_ann: Ann, current_ann: Ann
) -> Ann
    if og_ann and new_ann.prefix == og_ann.prefix and new_ann.as_path == og_ann.as_path and og_ann.recv_relationship != Relationships.ORIGIN:
        # Withdrawal exists in the local RIB, so remove it and reset current ann
        self.local_rib.pop(new_ann.prefix)
        # Current_ann was the ann we just withdrew, so set it to None
        if current_ann == og_ann:
            current_ann = None
        # Get the new best ann thus far
        return self._get_best_ann_by_gao_rexford(
            current_ann,
            self._get_and_process_best_ribs_in_ann(prefix)
        )
    return current_ann


def _withdraw_ann_from_neighbors(self: "BGPFull", withdraw_ann: "Ann") -> None:
    """Withdraw a route from all neighbors.

    This function will not remove an announcement from the local rib, that
    should be done before calling this function.

    Note that withdraw_ann is a deep copied ann
    """
    assert withdraw_ann.withdraw is True
    # Check ribs_out to see where the withdrawn ann was sent
    for send_neighbor in self.ribs_out.neighbors():
        # Delete ann from ribs out
        self.ribs_out.remove_entry(send_neighbor, withdraw_ann.prefix)
        self.send_q.add_ann(send_neighbor, withdraw_ann)


def _select_best_ribs_in(self: "BGPFull", prefix: str) -> Optional["Ann"]:
    """Selects best ann from ribs in (remember, RIBsIn is unprocessed"""

    # Get the best announcement
    best_ann: Ann | None = None
    for ann_info in self.ribs_in.get_ann_infos(prefix):
        best_ann = self._get_new_best_ann(
            current_ann, ann_info.unprocessed_ann, ann_info.recv_relationship
        )
    return best_ann
