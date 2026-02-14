from typing import TYPE_CHECKING

from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine import Announcement as Ann


class ROV(BGP):
    """An Policy that deploys ROV"""

    name: str = "ROV"

    def _valid_ann(self, ann: "Ann", recv_rel: "Relationships") -> bool:
        """Returns announcement validity

        Returns false if invalid by roa,
        otherwise uses standard BGP (such as no loops, etc)
        to determine validity
        """

        # Invalid by ROA is not valid by ROV
        if self.ann_is_invalid_by_roa(ann):
            return False
        # Use standard BGP to determine if the announcement is valid
        else:
            return super()._valid_ann(ann, recv_rel)
