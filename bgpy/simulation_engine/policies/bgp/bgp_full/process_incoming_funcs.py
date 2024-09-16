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

    for prefix, anns in self.recv_q.items():
        # Get announcement currently in local rib
        local_rib_ann: Ann | None = self.local_rib.get(prefix)
        current_ann: Ann | None = local_rib_ann
        current_processed: bool = True

        # Announcement will never be overriden, so continue
        if getattr(current_ann, "seed_asn", None):
            continue
        # For each announcement that is incoming
        for ann in anns:
            # withdrawals
            err = "Recieved two withdrawals from the same neighbor"
            assert len([x.as_path[0] for x in anns if x.withdraw]) == len(
                {x.as_path[0] for x in anns if x.withdraw}
            ), err

            err = (
                f"{self.as_.asn} Recieved two NON withdrawals "
                f"from the same neighbor {anns}"
            )
            assert len(
                [(x.as_path[0], x.next_hop_asn) for x in anns if not x.withdraw]
            ) == len(
                {(x.as_path[0], x.next_hop_asn) for x in anns if not x.withdraw}
            ), err

            # Always add to ribs in if it's not a withdrawal
            if not ann.withdraw:
                err = (
                    "you should never be replacing anns. "
                    "You should always withdraw first, "
                    "have it be blank, then add the new one"
                )
                assert (
                    self.ribs_in.get_unprocessed_ann_recv_rel(ann.as_path[0], prefix)
                    is None
                ), str(self.as_.asn) + " " + str(ann) + err

                self.ribs_in.add_unprocessed_ann(ann, from_rel)
            # Process withdrawals even for invalid anns in the ribs_in
            if ann.withdraw:
                if self._process_incoming_withdrawal(ann, from_rel):
                    # the above will return true if the local rib is changed
                    updated_loc_rib_ann: Ann | None = self.local_rib.get(prefix)
                    if current_processed:
                        current_ann = updated_loc_rib_ann
                    else:
                        assert updated_loc_rib_ann, "mypy type check"
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

        if local_rib_ann is not None and local_rib_ann is not current_ann:
            # Best ann has already been processed

            withdraw_ann: Ann = local_rib_ann.copy(
                overwrite_default_kwargs={"withdraw": True, "seed_asn": None}
            )

            self._withdraw_ann_from_neighbors(withdraw_ann)
            err = f"withdrawing ann that is same as new ann {withdraw_ann}"
            if not current_processed:
                assert current_ann is not None, "mypy type check"
                assert not withdraw_ann.prefix_path_attributes_eq(
                    self._copy_and_process(current_ann, from_rel)
                ), err

        # We have a new best!
        if current_processed is False:
            assert current_ann is not None, "mypy type check"
            current_ann = self._copy_and_process(current_ann, from_rel)
            # Save to local rib
            self.local_rib.add_ann(current_ann)

    self._reset_q(reset_q)


def _new_ann_better(
    self: "BGPFull",
    # Current announcement to check against
    current_ann: Optional["Ann"],
    # Whether or not current ann has been processed local rib
    # or if it resides in the ribs in
    current_processed: bool,
    # Default recv relationship if current ann is unprocessed
    default_current_recv_rel: "Relationships",
    # New announcement
    new_ann: Optional["Ann"],
    # If new announcement is in local rib, this is True
    new_processed: bool,
    # Default recv rel if new ann is unprocessed
    default_new_recv_rel: "Relationships",
) -> bool:
    """Determines if the new ann > current ann by Gao Rexford

    current_ann: Announcement we are checking against
    current_processed: True if announcement was processed (in local rib)
        This means that the announcement has the current as preprended
            to the AS path, and the proper recv_relationship set
    default_current_recv_rel:: Relationship for if the ann is unprocessed
    new_ann: New announcement
    new_processed: True if announcement was processed (in local rib)
        This means that the announcement has the current AS prepended
            to the AS path, and the proper recv_relationship set
    default_new_recv_rel: Relationship for if the ann is unprocessed
    """

    if current_ann is None:
        return True
    elif new_ann is None:
        return False

    if not current_processed:
        current_ann = self._copy_and_process(current_ann, default_current_recv_rel)
    if not new_processed:
        new_ann = self._copy_and_process(new_ann, default_new_recv_rel)

    return bool(self._get_best_ann_by_gao_rexford(current_ann, new_ann) == new_ann)


def _process_incoming_withdrawal(
    self: "BGPFull",
    ann: "Ann",
    recv_relationship: "Relationships",
) -> bool:
    prefix: str = ann.prefix
    neighbor: int = ann.as_path[0]
    # Return if the current ann was seeded (for an attack)
    local_rib_ann = self.local_rib.get(prefix)

    err: str = "Trying to withdraw seeded ann {local_rib_ann.seed_asn}"
    assert not (
        (local_rib_ann is not None)
        and (
            (ann.prefix_path_attributes_eq(local_rib_ann))
            and (local_rib_ann.seed_asn is not None)
        )
    ), err

    ann_info: AnnInfo | None = self.ribs_in.get_unprocessed_ann_recv_rel(
        neighbor, prefix
    )
    # I don't remember why this could be None... this assert may be wrong
    assert ann_info is not None, "for mypy"
    current_ann_ribs_in = ann_info.unprocessed_ann

    err = (
        f"Cannot withdraw ann that was never sent.\n\t "
        f"Ribs in: {current_ann_ribs_in}\n\t withdraw: {ann}"
    )
    assert ann.prefix_path_attributes_eq(current_ann_ribs_in), err

    # Remove ann from Ribs in
    self.ribs_in.remove_entry(neighbor, prefix)

    # Remove ann from local rib
    withdraw_ann: Ann = self._copy_and_process(
        ann, recv_relationship, overwrite_default_kwargs={"withdraw": True}
    )
    if withdraw_ann.prefix_path_attributes_eq(self.local_rib.get(prefix)):
        self.local_rib.pop(prefix, None)
        # Also remove from neighbors
        self._withdraw_ann_from_neighbors(withdraw_ann)

        best_ann: Ann | None = self._select_best_ribs_in(prefix)

        # Put new ann in local rib
        if best_ann is not None:
            self.local_rib.add_ann(best_ann)

        err = "Best ann should not be identical to the one we just withdrew"
        assert not withdraw_ann.prefix_path_attributes_eq(best_ann), err
        return True
    return False


def _withdraw_ann_from_neighbors(self: "BGPFull", withdraw_ann: "Ann") -> None:
    """Withdraw a route from all neighbors.

    This function will not remove an announcement from the local rib, that
    should be done before calling this function.

    Note that withdraw_ann is a deep copied ann
    """
    assert withdraw_ann.withdraw is True
    # Check ribs_out to see where the withdrawn ann was sent
    for send_neighbor in self.ribs_out.neighbors():
        # If the two announcements are equal
        if withdraw_ann.prefix_path_attributes_eq(
            self.ribs_out.get_ann(send_neighbor, withdraw_ann.prefix)
        ):
            # Delete ann from ribs out
            self.ribs_out.remove_entry(send_neighbor, withdraw_ann.prefix)
            self.send_q.add_ann(send_neighbor, withdraw_ann)

    # We may not have sent the ann yet, it may just be in the send queue
    # and not ribs out
    # We want to cancel out any anns in the send_queue that match the wdraw
    for neighbor_obj in self.as_.neighbors:
        send_info: SendInfo | None = self.send_q.get_send_info(
            neighbor_obj, withdraw_ann.prefix
        )
        if send_info is None or send_info.ann is None:
            continue
        elif send_info.ann.prefix_path_attributes_eq(withdraw_ann):
            send_info.ann = None


def _select_best_ribs_in(self: "BGPFull", prefix: str) -> Optional["Ann"]:
    """Selects best ann from ribs in

    Remember, ribs in anns are NOT deep copied
    """

    # Get the best announcement
    best_unprocessed_ann: Ann | None = None
    best_recv_relationship: Relationships | None = None
    for ann_info in self.ribs_in.get_ann_infos(prefix):
        new_unprocessed_ann = ann_info.unprocessed_ann
        new_recv_relationship = ann_info.recv_relationship
        if self._new_ann_better(
            best_unprocessed_ann,
            False,
            best_recv_relationship,  # type: ignore
            new_unprocessed_ann,
            False,
            new_recv_relationship,
        ):
            best_unprocessed_ann = new_unprocessed_ann
            best_recv_relationship = new_recv_relationship

    if best_unprocessed_ann is not None:
        assert best_recv_relationship is not None, "mypy type check"
        return self._copy_and_process(best_unprocessed_ann, best_recv_relationship)
    else:
        return None
