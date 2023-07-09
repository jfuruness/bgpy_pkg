from typing import Optional, TYPE_CHECKING


from bgpy.simulation_engine.ann_containers import AnnInfo, SendInfo

from bgpy.simulation_engine.announcement import Announcement as Ann
from bgpy.enums import Relationships


if TYPE_CHECKING:
    from bgpy.simulation_framework import Scenario


def process_incoming_anns(
    self,
    *,
    from_rel: Relationships,
    propagation_round: int,
    # Usually None for attack
    scenario: "Scenario",
    reset_q: bool = True,
):
    """Process all announcements that were incoming from a specific rel"""

    for prefix, anns in self._recv_q.prefix_anns():
        # Get announcement currently in local rib
        _local_rib_ann: Optional[Ann] = self._local_rib.get_ann(prefix)
        current_ann: Optional[Ann] = _local_rib_ann
        current_processed: bool = True

        # Announcement will never be overriden, so continue
        if getattr(current_ann, "seed_asn", None):
            continue
        # For each announcement that is incoming
        for ann in anns:
            # withdrawals
            err = "Recieved two withdrawals from the same neighbor"
            assert len([x.as_path[0] for x in anns if x.withdraw]) == len(
                set([x.as_path[0] for x in anns if x.withdraw])
            ), err

            err = "Recieved two NON withdrawals from the same neighbor"
            assert len([x.as_path[0] for x in anns if not x.withdraw]) == len(
                set([x.as_path[0] for x in anns if not x.withdraw])
            ), err

            # Always add to ribs in if it's not a withdrawal
            if not ann.withdraw:
                err = (
                    "you should never be replacing anns. "
                    "You should always withdraw first, "
                    "have it be blank, then add the new one"
                )
                assert (
                    self._ribs_in.get_unprocessed_ann_recv_rel(ann.as_path[0], prefix)
                    is None
                ), (str(self.asn) + " " + str(ann) + err)

                self._ribs_in.add_unprocessed_ann(ann, from_rel)
            # Process withdrawals even for invalid anns in the ribs_in
            if ann.withdraw:
                if self._process_incoming_withdrawal(ann, from_rel):
                    # the above will return true if the local rib is changed
                    updated_loc_rib_ann: Ann = self._local_rib.get_ann(prefix)
                    if current_processed:
                        current_ann = updated_loc_rib_ann
                    else:
                        new_ann_is_better: bool = self._new_ann_better(
                            current_ann,
                            current_processed,
                            from_rel,
                            updated_loc_rib_ann,
                            True,
                            updated_loc_rib_ann.recv_relationship,
                        )
                        if new_ann_is_better:
                            current_ann = updated_loc_rib_ann
                            current_processed = True

            # If it's valid, process it
            elif self._valid_ann(ann, from_rel):
                new_ann_is_better = self._new_ann_better(
                    current_ann, current_processed, from_rel, ann, False, from_rel
                )

                # If the new priority is higher
                if new_ann_is_better:
                    current_ann = ann
                    current_processed = False

        if _local_rib_ann is not None and _local_rib_ann is not current_ann:
            # Best ann has already been processed

            withdraw_ann: Ann = _local_rib_ann.copy(
                overwrite_default_kwargs={"withdraw": True}
            )

            self._withdraw_ann_from_neighbors(withdraw_ann)
            err = f"withdrawing ann that is same as new ann {withdraw_ann}"
            if not current_processed:
                assert not withdraw_ann.prefix_path_attributes_eq(
                    self._copy_and_process(current_ann, from_rel)
                ), err

        # We have a new best!
        if current_processed is False:
            current_ann = self._copy_and_process(current_ann, from_rel)
            # Save to local rib
            self._local_rib.add_ann(current_ann)

    self._reset_q(reset_q)


def _process_incoming_withdrawal(
    self, ann: Ann, recv_relationship: Relationships
) -> bool:
    prefix: str = ann.prefix
    neighbor: int = ann.as_path[0]
    # Return if the current ann was seeded (for an attack)
    _local_rib_ann = self._local_rib.get_ann(prefix)

    err: str = "Trying to withdraw seeded ann {_local_rib_ann.seed_asn}"
    assert not (
        (_local_rib_ann is not None)
        and (
            (ann.prefix_path_attributes_eq(_local_rib_ann))
            and (_local_rib_ann.seed_asn is not None)
        )
    ), err

    ann_info: Optional[AnnInfo] = self._ribs_in.get_unprocessed_ann_recv_rel(
        neighbor, prefix
    )
    current_ann_ribs_in = ann_info.unprocessed_ann  # type: ignore

    err = (
        f"Cannot withdraw ann that was never sent.\n\t "
        f"Ribs in: {current_ann_ribs_in}\n\t withdraw: {ann}"
    )
    assert ann.prefix_path_attributes_eq(current_ann_ribs_in), err

    # Remove ann from Ribs in
    self._ribs_in.remove_entry(neighbor, prefix)

    # Remove ann from local rib
    withdraw_ann: Ann = self._copy_and_process(
        ann, recv_relationship, overwrite_default_kwargs={"withdraw": True}
    )
    if withdraw_ann.prefix_path_attributes_eq(self._local_rib.get_ann(prefix)):
        self._local_rib.remove_ann(prefix)
        # Also remove from neighbors
        self._withdraw_ann_from_neighbors(withdraw_ann)

        best_ann: Optional[Ann] = self._select_best_ribs_in(prefix)

        # Put new ann in local rib
        if best_ann is not None:
            self._local_rib.add_ann(best_ann)

        err = "Best ann should not be identical to the one we just withdrew"
        assert not withdraw_ann.prefix_path_attributes_eq(best_ann), err
        return True
    return False


def _withdraw_ann_from_neighbors(self, withdraw_ann: Ann):
    """Withdraw a route from all neighbors.

    This function will not remove an announcement from the local rib, that
    should be done before calling this function.

    Note that withdraw_ann is a deep copied ann
    """
    assert withdraw_ann.withdraw is True
    # Check ribs_out to see where the withdrawn ann was sent
    for send_neighbor in self._ribs_out.neighbors():
        # If the two announcements are equal
        if withdraw_ann.prefix_path_attributes_eq(
            self._ribs_out.get_ann(send_neighbor, withdraw_ann.prefix)
        ):
            # Delete ann from ribs out
            self._ribs_out.remove_entry(send_neighbor, withdraw_ann.prefix)
            self._send_q.add_ann(send_neighbor, withdraw_ann)

    # We may not have sent the ann yet, it may just be in the send queue
    # and not ribs out
    # We want to cancel out any anns in the send_queue that match the wdraw
    for neighbor_obj in self.neighbors:
        send_info: Optional[SendInfo] = self._send_q.get_send_info(
            neighbor_obj, withdraw_ann.prefix
        )
        if send_info is None or send_info.ann is None:
            continue
        elif send_info.ann.prefix_path_attributes_eq(withdraw_ann):
            send_info.ann = None


def _select_best_ribs_in(self, prefix: str) -> Optional[Ann]:
    """Selects best ann from ribs in

    Remember, ribs in anns are NOT deep copied"""

    # Get the best announcement
    best_unprocessed_ann: Optional[Ann] = None
    best_recv_relationship: Optional[Relationships] = None
    for ann_info in self._ribs_in.get_ann_infos(prefix):
        new_unprocessed_ann = ann_info.unprocessed_ann
        new_recv_relationship = ann_info.recv_relationship
        if self._new_ann_better(
            best_unprocessed_ann,
            False,
            best_recv_relationship,
            new_unprocessed_ann,
            False,
            new_recv_relationship,
        ):
            best_unprocessed_ann = new_unprocessed_ann
            best_recv_relationship = new_recv_relationship

    if best_unprocessed_ann is not None:
        # mypy having trouble dealing with this
        return self._copy_and_process(  # type: ignore
            best_unprocessed_ann, best_recv_relationship
        )
    else:
        return None
