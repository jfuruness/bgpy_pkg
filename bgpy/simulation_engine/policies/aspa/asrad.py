
from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships
from .asra import ASRA

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ASRAD(ASRA):
    name = "ASRAD"

    @property
    def UP_SLACK(self) -> int:
        return 0

    @property
    def DOWN_SLACK(self) -> int:
        return 0

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:
        # 1) run ASPA + ASRA first
        if not super()._valid_ann(ann, from_rel):
            return False

        as_graph = self.as_.as_graph
        path = ann.as_path[::-1]
        n = len(path)

        # 2) per-AS depth check, but ONLY for ASRAD adopters
        for i, asn in enumerate(path):
            as_obj = as_graph.as_dict.get(asn)
            if not as_obj:
                continue

            # only enforce if this AS adopts ASRAD (or subclass)
            if not isinstance(as_obj.policy, ASRAD):
                continue

            max_provider_depth = getattr(
                as_obj,
                "max_provider_depth",
                getattr(as_obj, "max_provider_height", None),
            )
            max_customer_depth = getattr(as_obj, "max_customer_depth", None)

            # upward (toward receiver)
            up_len = 0
            for j in range(i, n - 1):
                if not self._provider_check(path[j], path[j + 1]):
                    break
                up_len += 1

            # downward (toward origin)
            down_len = 0
            for j in range(i, 0, -1):
                if not self._provider_check(path[j], path[j - 1]):
                    break
                down_len += 1

            # peer inflation: assume at most 1 → subtract 1
            adj_down_len = max(down_len - 1, 0)

            if max_provider_depth is not None:
                if up_len > max_provider_depth + self.UP_SLACK:
                    return False

            if max_customer_depth is not None:
                if adj_down_len > max_customer_depth + self.DOWN_SLACK:
                    return False

        return True


class ASRAD1(ASRAD):
    name = "ASRAD1"
    UP_SLACK = 1
    DOWN_SLACK = 1


class ASRAD2(ASRAD):
    name = "ASRAD2"
    UP_SLACK = 2
    DOWN_SLACK = 2
