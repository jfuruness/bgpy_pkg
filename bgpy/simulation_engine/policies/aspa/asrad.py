from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships
from .asra import ASRA

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ASRAD(ASRA):
    name = "ASRAD"

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:
        # 1) run ASPA + ASRA first
        if not super()._valid_ann(ann, from_rel):
            return False

        cur_as = self.as_
        max_customer_depth = getattr(cur_as, "max_customer_depth", 0)
        max_provider_depth = getattr(cur_as, "max_provider_depth", 0)

        # 2) ASPA’s original ramps
        max_up_ramp = self._get_max_up_ramp_length(ann)
        max_down_ramp = self._get_max_down_ramp_length(ann)

        # 3) down-ramp can be inflated by 1 if there was a peer → discount 1
        adj_down_ramp = max(max_down_ramp - 1, 0)

        # 4) compare
        # up: normal
        if max_up_ramp > max_provider_depth + self._UP_SLACK:
            return False

        # down: use adjusted ramp
        if adj_down_ramp > max_customer_depth + self._DOWN_SLACK:
            return False

        return True

    @property
    def UP_SLACK(self) -> int:
        return 0
    @property
    def DOWN_SLACK(self) -> int:
        return 0

class ASRAD1:
    UP_SLACK = 1
    DOWN_SLACK = 1

class ASRAD2:
    UP_SLACK = 2
    DOWN_SLACK = 2
