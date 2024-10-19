from typing import TYPE_CHECKING

from .edge_filter import EdgeFilter

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine import Announcement as Ann


class ROVEdgeFilter(EdgeFilter):
    """Prevents edge ASes from paths containing ASNs they don't own (w/ROV)"""

    name: str = "ROV + EdgeFilter"

    def _valid_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """ROV+EdgeFilter"""

        return (
            False
            if self.ann_is_invalid_by_roa(ann)
            else super()._valid_ann(ann, from_rel)
        )
