from typing import Any, Callable, Optional, TYPE_CHECKING

from bgpy.simulation_engine.policies.bgp.bgp_policy import BGPPolicy

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann


class BGPSecPolicy(BGPPolicy):
    """Represents BGPSec

    Since there are no real world implementations,
    we assume a secure path preference of security third,
    or else this would literally do nothing lmao
    """

    name = "BGPSec"

    def seed_ann(self, ann: "Ann") -> None:  # type: ignore
        """Seeds announcement at this AS and initializes BGPSec path"""

        super().seed_ann(ann.copy({"bgpsec_as_path": ann.as_path}))

    def policy_propagate(  # type: ignore
        self, neighbor: "AS", ann: "Ann", *args, **kwargs
    ) -> bool:
        """Sets BGPSec fields when propagating

        If sending to bgpsec, set next_as and keep bgpsec_as_path
        otherwise clear out both fields
        """

        next_asn = neighbor.asn if isinstance(neighbor.policy, BGPSecPolicy) else None
        path = ann.bgpsec_path if isinstance(neighbor.policy, BGPSecPolicy) else ()
        send_ann = ann.copy({"bgpsec_next_asn": next_asn, "bgpsec_as_path": path})
        neighbor.policy.recieve_ann(send_ann)

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

        overwrite_default_kwargs["bgsec_as_path"] = overwrite_default_kwargs.get(
            "bgpsec_as_path", bgpsec_as_path
        )

        return super()._copy_and_process(
            ann, recv_relationship, overwrite_default_kwargs
        )

    # mypy wants a return statement, but nah
    def _get_best_ann_by_bgpsec(  # type: ignore
        self, current_ann: "Ann", new_ann: "Ann"
    ) -> Optional["Ann"]:
        current_valid = current_ann.bgpsec_valid(self.as_.asn)
        new_valid = new_ann.bgpsec_valid(self.as_.asn)

        if current_valid and not new_valid:
            return current_ann
        elif not current_valid and new_valid:
            return new_ann

    @property
    def _gao_rexford_funcs(
        self,
    ) -> tuple[Callable[["Ann", "Ann"], Optional["Ann"]], ...]:
        return (
            self._get_best_ann_by_local_pref,
            self._get_best_ann_by_as_path,
            self._get_best_ann_by_bgpsec,
            self._get_best_ann_by_lowest_neighbor_asn_tiebreaker,
        )
