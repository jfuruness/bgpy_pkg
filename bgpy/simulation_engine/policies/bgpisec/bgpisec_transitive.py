from typing import TYPE_CHECKING, Any

from bgpy.simulation_engine.policies.bgp import BGP
from bgpy.simulation_engine.policies.bgpsec import BGPSec

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann


class BGPiSecTransitive(BGPSec):
    """Represents BGPiSec Transitive attributes"""

    name = "BGP-iSec Transitive Only"

    # Doesn't change the path preference mechanism so that it's easier to deploy
    # and path preference has no benefit
    # as shown in the bgp-isec paper
    # this also follows their recommendation
    # Suppress this. Just using a mixin rather than some weird OO inheritance
    _get_best_ann_by_gao_rexford = BGP._get_best_ann_by_gao_rexford  # noqa: SLF001

    def _policy_propagate(
        self,
        neighbor: "AS",
        ann: "Ann",
        propagate_to: "Relationships",
        send_rels: set["Relationships"],
    ) -> bool:
        """Sets BGPSec fields when propagating"""

        send_ann = ann.copy(
            {"bgpsec_next_asn": neighbor.asn, "bgpsec_as_path": ann.bgpsec_as_path}
        )
        self._process_outgoing_ann(neighbor, send_ann, propagate_to, send_rels)
        return True

    def _copy_and_process(
        self,
        ann: "Ann",
        recv_relationship: "Relationships",
        overwrite_default_kwargs: dict[Any, Any] | None = None,
    ) -> "Ann":
        """Sets the bgpsec_as_path.

        prepends ASN if valid, otherwise clears
        """
        bgpsec_as_path = (self.as_.asn, *ann.bgpsec_as_path)

        if overwrite_default_kwargs is None:
            overwrite_default_kwargs = {}

        overwrite_default_kwargs["bgpsec_as_path"] = overwrite_default_kwargs.get(
            "bgpsec_as_path", bgpsec_as_path
        )

        return super()._copy_and_process(
            ann, recv_relationship, overwrite_default_kwargs
        )

    def _valid_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """Determines bgp-isec transitive validity and super() validity"""

        bgpisec_transitive_valid = self._bgpisec_transitive_valid_ann(ann, from_rel)
        return bgpisec_transitive_valid and super()._valid_ann(ann, from_rel)

    def _bgpisec_transitive_valid_ann(
        self,
        ann: "Ann",
        from_rel: "Relationships",
    ) -> bool:
        """Determines bgp-isec transitive validity

        If any ASes along the AS path are adopting and are not in the bgpsec_as_path,
        that means those ASes didn't add signatures, therefore the ann is missing
        signatures and should be dropped
        """

        as_graph = self.as_.as_graph
        bgpsec_signatures = ann.bgpsec_as_path
        for asn in ann.as_path:
            if asn not in bgpsec_signatures and isinstance(
                as_graph.as_dict[asn].policy, BGPiSecTransitive
            ):
                return False
        return True
