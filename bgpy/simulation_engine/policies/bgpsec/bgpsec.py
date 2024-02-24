from typing import Any, Optional, TYPE_CHECKING

from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann


class BGPSec(BGP):
    """Represents BGPSec

    Since there are no real world implementations,
    we assume a secure path preference of security third,
    which is in line with the majority of users
    for the survey results in "A Survey of Interdomain Routing Policies"
    https://www.cs.bu.edu/~goldbe/papers/survey.pdf
    """

    name = "BGPSec"

    def seed_ann(self, ann: "Ann") -> None:  # type: ignore
        """Seeds announcement at this AS and initializes BGPSec path"""

        # This ann is valid, add the bgpsec as path
        if ann.as_path == (self.as_.asn,):
            ann = ann.copy({"bgpsec_as_path": ann.as_path})
        super().seed_ann(ann)

    def _policy_propagate(  # type: ignore
        self, neighbor: "AS", ann: "Ann", *args, **kwargs
    ) -> bool:
        """Sets BGPSec fields when propagating

        If sending to bgpsec, set next_as and keep bgpsec_as_path
        otherwise clear out both fields
        """

        if isinstance(neighbor.policy, BGPSec):
            next_asn = neighbor.asn
            path = ann.bgpsec_as_path
        else:
            next_asn = None
            path = ()
        send_ann = ann.copy({"bgpsec_next_asn": next_asn, "bgpsec_as_path": path})
        self._process_outgoing_ann(neighbor, send_ann, *args, **kwargs)
        return True

    # Mypy doesn't understand the superclass
    def _copy_and_process(  # type: ignore
        self,
        ann: "Ann",
        recv_relationship: "Relationships",
        overwrite_default_kwargs: Optional[dict[Any, Any]] = None,
    ) -> "Ann":
        """Sets the bgpsec_as_path.

        prepends ASN if valid, otherwise clears
        """
        if ann.bgpsec_valid(self.as_.asn):
            bgpsec_as_path = (self.as_.asn,) + ann.bgpsec_as_path
        else:
            bgpsec_as_path = ()

        if overwrite_default_kwargs is None:
            overwrite_default_kwargs = {}

        overwrite_default_kwargs["bgpsec_as_path"] = overwrite_default_kwargs.get(
            "bgpsec_as_path", bgpsec_as_path
        )

        return super()._copy_and_process(
            ann, recv_relationship, overwrite_default_kwargs
        )

    def _get_best_ann_by_bgpsec(
        self, current_ann: "Ann", new_ann: "Ann"
    ) -> Optional["Ann"]:
        current_valid = current_ann.bgpsec_valid(self.as_.asn)
        new_valid = new_ann.bgpsec_valid(self.as_.asn)

        if current_valid and not new_valid:
            return current_ann
        elif not current_valid and new_valid:
            return new_ann
        else:
            return None

    def _get_best_ann_by_gao_rexford(  # type: ignore
        self,
        current_ann: Optional["Ann"],
        new_ann: "Ann",
    ) -> "Ann":
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
                    ann = self._get_best_ann_by_bgpsec(current_ann, new_ann)
                    if ann:
                        return ann
                    else:
                        return self._get_best_ann_by_lowest_neighbor_asn_tiebreaker(
                            current_ann, new_ann
                        )
            raise Exception("No ann was chosen")
