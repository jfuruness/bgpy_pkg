from typing import Optional

from bgpy.simulation_engine.announcement import Announcement as Ann


def _get_best_ann_by_gao_rexford(
    self,
    current_ann: Optional[Ann],
    new_ann: Ann,
) -> Ann:
    """Determines if the new ann > current ann by Gao Rexford"""

    assert new_ann is not None, "New announcement can't be None"

    if current_ann is None:
        return new_ann
    else:
        # Inspiration for this func refactor came from bgpsecsim
        for func in self._gao_rexford_funcs:
            best_ann = func(current_ann, new_ann)
            if best_ann is not None:
                return best_ann
        raise Exception("No ann was chosen")


def _get_best_ann_by_local_pref(
    self, current_ann: Ann, new_ann: Ann
) -> Optional[Ann]:
    """Returns best announcement by local pref, or None if tie"""

    if current_ann.recv_relationship.value > new_ann.recv_relationship.value:
        return current_ann
    elif current_ann.recv_relationship.value < new_ann.recv_relationship.value:
        return new_ann
    else:
        return None


def _get_best_ann_by_as_path(
    self, current_ann: Ann, new_ann: Ann
) -> Optional[Ann]:
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
    self, current_ann: Ann, new_ann: Ann
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
