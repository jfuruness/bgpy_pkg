from typing import TYPE_CHECKING

from bgpy.shared.exceptions import GaoRexfordError
from bgpy.simulation_engine.announcement import Announcement as Ann

if TYPE_CHECKING:
    from .bgp import BGP


def _get_best_ann_by_gao_rexford(
    self: "BGP",
    current_ann: Ann | None,
    new_ann: Ann,
) -> Ann:
    """Determines if the new ann > current ann by Gao Rexford"""

    assert new_ann is not None, "New announcement can't be None"

    if current_ann is None:
        return new_ann
    else:
        # Inspiration for this func refactor came from bgpsecsim
        # for func in self._gao_rexford_funcs:
        #     best_ann = func(current_ann, new_ann)
        #     if best_ann is not None:
        #         assert isinstance(best_ann, Ann), "mypy type check"
        #         return best_ann

        # Having this dynamic like above is literally 7x slower, resulting
        # in bottlenecks. Gotta do it the ugly way unfortunately
        ann = self._get_best_ann_by_local_pref(current_ann, new_ann)
        if ann:
            return ann
        else:
            ann = self._get_best_ann_by_as_path(current_ann, new_ann)
            if ann:
                return ann
            else:
                return self._get_best_ann_by_lowest_neighbor_asn_tiebreaker(
                    current_ann, new_ann
                )
        raise GaoRexfordError("No ann was chosen")


def _get_best_ann_by_local_pref(
    self: "BGP", current_ann: Ann, new_ann: Ann
) -> Ann | None:
    """Returns best announcement by local pref, or None if tie"""

    if current_ann.recv_relationship.value > new_ann.recv_relationship.value:
        return current_ann
    elif current_ann.recv_relationship.value < new_ann.recv_relationship.value:
        return new_ann
    else:
        return None


def _get_best_ann_by_as_path(self: "BGP", current_ann: Ann, new_ann: Ann) -> Ann | None:
    """Returns best announcement by as path length, or None if tie

    Shorter AS Paths are better
    """

    if len(current_ann.as_path) < len(new_ann.as_path):
        return current_ann
    elif len(current_ann.as_path) > len(new_ann.as_path):
        return new_ann
    else:
        return None


def _get_best_ann_by_lowest_neighbor_asn_tiebreaker(
    self: "BGP", current_ann: Ann, new_ann: Ann
) -> Ann:
    """Determines if the new ann > current ann by Gao Rexford for ties

    This breaks ties by lowest asn of the neighbor sending the announcement
    So if the two announcements are from the same nieghbor, return current ann
    """

    current_neighbor_asn = current_ann.as_path[min(len(current_ann.as_path), 1)]
    new_neighbor_asn = new_ann.as_path[min(len(new_ann.as_path), 1)]

    if current_neighbor_asn <= new_neighbor_asn:
        return current_ann
    else:
        return new_ann
