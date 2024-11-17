from typing import TYPE_CHECKING

from .enforce_first_as import EnforceFirstAS

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine import Announcement as Ann


class ROVEnforceFirstAS(EnforceFirstAS):
    """Deploys Enforce-First-AS + ROV

    On most routers this checks that the first ASN in the AS-Path is a neighbor
    This is used in ASPA based on the ASPA RFC
    """

    name: str = "ROV + Enforce-First-AS"

    def _valid_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """Returns False if first ASN is not a neighbor (or invalid ROV), else True"""

        return (
            False
            if self.ann_is_invalid_by_roa(ann)
            else super()._valid_ann(ann, from_rel)
        )
