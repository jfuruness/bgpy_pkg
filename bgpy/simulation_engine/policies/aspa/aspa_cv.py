from typing import TYPE_CHECKING

from bgpy.simulation_engine import ASRA, ProviderConeID

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann


class ASPACV(ASRA):
    """Esentially ASPA and checking neighbors at every AS together"""

    name = "ASPA-CV"

    def _valid_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """Combines ASPA valid and checking neighbors at every AS"""

        # Ignore private access, just trying to use mixins instead of crazy inheritance
        provider_cone_valid = ProviderConeID._provider_cone_valid(  # noqa: SLF001
            self, ann, from_rel
        )
        return provider_cone_valid and super()._valid_ann(ann, from_rel)
