from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.ann_containers import AnnInfo, SendInfo
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_framework import Scenario

    from .bgp_full import BGPFull


# NOTE: For all validation funcs, we assert, but also return True
# this way, in the code that calls this function, we can call these with assert
# so that they get ignored when run with pypy3 -O to ignore the overhead
# of the function calls, but we don't need to clutter the main code with the msg

def only_one_withdrawal_per_prefix_per_neighbor(self, anns: list["Ann"]) -> bool:
    """Ensures that neighbor didn't send two withdrawals for same prefix"""
    assert (
        len([x.as_path[0] for x in anns if x.withdraw])
        == len({x.as_path[0] for x in anns if x.withdraw})
        and self.error_on_invalid_routes
    ), "More than one withdrawal per prefix from the same neighbor"
    return True


def only_one_ann_per_prefix_per_neighbor(self, anns: list["Ann"]) -> bool:
    """Ensures that neighbor didn't send two anns for same prefix"""

    err = (
        f"{self.as_.asn} Recieved two NON withdrawals "
        f"from the same neighbor {anns}"
    )
    assert (
        len([(x.as_path[0], x.next_hop_asn) for x in anns if not x.withdraw])
        == len({(x.as_path[0], x.next_hop_asn) for x in anns if not x.withdraw})
        and self.error_on_invalid_routes
    ), err
    return True


def no_implicit_withdrawals(self, ann: "Ann", prefix: str) -> bool:
    """Ensures that you withdraw, then add a new ann

    Ensures that no ann is overwritten by another ann, anns can only be
    overwritten by withdrawals
    """

    err = "Ann {ann} overwrote local RIB. You should withdraw first, then add new ann"
    assert (
            self.ribs_in.get_unprocessed_ann_recv_rel(ann.as_path[0], prefix) is None
    ) and self.error_on_invalid_routes, str(self.as_.asn) + " " + str(ann) + err
    return True


def not_withdrawing_new_ann(self, withdraw_ann, current_ann, from_rel) -> bool:
    """Ensures that we aren't withdrawing an ann that came from recv_q this round"""

    err = f"withdrawing ann that is same as new ann {withdraw_ann}"
    assert (
        not withdraw_ann.prefix_path_attributes_eq(
            self._copy_and_process(current_ann, from_rel)
        )
        and self.error_on_invalid_routes
    ), err
    return True


def withdrawal_in_ribs_in(
    self, ann_info: AnnInfo, ann: "Ann", from_rel: Relationships
) -> bool:
    """Ensures that all withdrawals have an ann that exists in the RIBsIn"""

    err = (
        "Trying to withdraw ann that was never stored in RIBsIn "
        f"{self.as_.asn=} {ann_info=} {self.ribs_in=} {ann=} {from_rel=}"
    )
    assert ann_info is not None and self.error_on_invalid_routes, err

    current_ann_ribs_in = ann_info.unprocessed_ann
    assert (
        ann.prefix == current_ann_ribs_in.prefix and ann.as_path == current_ann.as_path
        and self.error_on_invalid_routes
    ), err

    return True


def best_ann_isnt_the_withdrawn_ann(
    self, withdraw_ann: "Ann", ann: "Ann"
) -> bool:

    err = "Best ann should not be identical to the one we just withdrew"
    assert (
        ann.prefix == current_ann_ribs_in.prefix and ann.as_path == current_ann.as_path
        and self.error_on_invalid_routes
    ), err
    return True
