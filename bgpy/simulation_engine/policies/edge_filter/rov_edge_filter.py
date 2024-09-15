from typing import TYPE_CHECKING

from .edge_filter import EdgeFilter

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.shared.enums import Relationships


class ROVEdgeFilter(EdgeFilter):
    """Prevents edge ASes from paths containing ASNs they don't own (w/ROV)"""

    name: str = "ROV + EdgeFilter"

    def _valid_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """ROV+EdgeFilter"""

        if ann.invalid_by_roa:
            return False
        else:
            return super()._valid_ann(ann, from_rel)
