from typing import TYPE_CHECKING, Any

from bgpy.simulation_engine.ann_containers import RecvQueue

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_framework import Scenario

    from .bgp import BGP


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
        # Get announcement currently in local rib
        current_ann: Ann | None = self.local_rib.get(prefix)
        og_ann = current_ann

        # Seeded Ann will never be overriden, so continue
        if getattr(current_ann, "seed_asn", None) is not None:
            continue
        # For each announcement that was incoming
        for new_ann in ann_list:
            # Make sure there are no loops
            # In ROV subclass also check roa validity
            if self._valid_ann(new_ann, from_rel):
                new_ann_processed = self._copy_and_process(new_ann, from_rel)

                current_ann = self._get_best_ann_by_gao_rexford(
                    current_ann, new_ann_processed
                )

        # This is a new best ann. Process it and add it to the local rib
        if og_ann != current_ann:
            assert current_ann, "mypy type check"
            assert current_ann.seed_asn in (None, self.as_.asn), "Seed ASN is wrong"
            # Save to local rib
            self.local_rib.add_ann(current_ann)

    self._reset_q(reset_q)


def _valid_ann(
    self: "BGP",
    ann: "Ann",
    recv_relationship: "Relationships",
) -> bool:
    """Determine if an announcement is valid or should be dropped"""

    # BGP Loop Prevention Check
    return self.as_.asn not in ann.as_path


def _copy_and_process(
    self: "BGP",
    ann: "Ann",
    recv_relationship: "Relationships",
    overwrite_default_kwargs: dict[Any, Any] | None = None,
) -> "Ann":
    """Deep copies ann and modifies attrs

    Prepends AS to AS Path and sets recv_relationship
    """

    kwargs: dict[str, Any] = {
        "as_path": (self.as_.asn, *ann.as_path),
        "recv_relationship": recv_relationship,
        "seed_asn": None,
    }

    if overwrite_default_kwargs:
        kwargs.update(overwrite_default_kwargs)
    # Don't use a dict comp here for speed
    return ann.copy(overwrite_default_kwargs=kwargs)


def _reset_q(self: "BGP", reset_q: bool) -> None:
    """Resets the recieve q"""

    if reset_q:
        self.recv_q = RecvQueue()
