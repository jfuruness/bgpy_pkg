from typing import Any, Optional, TYPE_CHECKING, Union

from bgpy.simulation_engines.py_simulation_engine.ann_containers import RecvQueue

if TYPE_CHECKING:
    from bgpy.enums import Relationships
    from bgpy.simulation_framework import Scenario
    from bgpy.simulation_engine.announcement import Announcement as Ann



def receive_ann(
    self, ann: Ann, accept_withdrawals: bool = False
) -> None:
    """Function for recieving announcements, adds to recv_q"""

    if getattr(ann, "withdraw", False) and not accept_withdrawals:
        raise NotImplementedError("Policy can't handle withdrawals")
    self._recv_q.add_ann(ann)


def process_incoming_anns(
    self,
    *,
    from_rel: Relationships,
    propagation_round: int,
    scenario: "Scenario",
    reset_q: bool = True,
) -> None:
    """Process all announcements that were incoming from a specific rel"""

    # For each prefix, get all anns recieved
    for prefix, ann_list in self._recv_q.prefix_anns():
        # Get announcement currently in local rib
        current_ann: Ann = self._local_rib.get_ann(prefix)
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
            # Save to local rib
            self._local_rib.add_ann(current_ann)

    self._reset_q(reset_q)


def _valid_ann(
    self,
    ann: Ann,
    recv_relationship: Relationships,
) -> bool:
    """Determine if an announcement is valid or should be dropped"""

    # BGP Loop Prevention Check
    return self.as_.asn not in ann.as_path


def _copy_and_process(
    self,
    ann: Ann,
    recv_relationship: Relationships,
    overwrite_default_kwargs: Optional[dict[Any, Any]] = None,
) -> Ann:
    """Deep copies ann and modifies attrs

    Prepends AS to AS Path and sets recv_relationship
    """

    kwargs: dict[str, Any] = {
        "as_path": (
            self.as_.asn,
        )
        + ann.as_path,
        "recv_relationship": recv_relationship,
    }

    if overwrite_default_kwargs:
        kwargs.update(overwrite_default_kwargs)
    # Don't use a dict comp here for speed
    return ann.copy(overwrite_default_kwargs=kwargs)


def _reset_q(self, reset_q: bool):
    """Resets the recieve q"""

    if reset_q:
        self._recv_q = RecvQueue()
