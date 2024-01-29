from dataclasses import dataclass
from typing import Optional

from bgpy.enums import ASGroups, Plane, Outcomes
from bgpy.simulation_engine import Policy


@dataclass(frozen=True, slots=True)
class MetricKey:
    """Key for storing data within each metric"""

    plane: Plane
    as_group: ASGroups
    outcome: Outcomes
    PolicyCls: Optional[type[Policy]] = None

    def __lt__(self, other) -> bool:
        """Used for sorting in metric tracker"""
        if isinstance(other, MetricKey):
            return (
                self.plane.value < other.plane.value
                and self.as_group.value < other.as_group.value
                and self.outcome.value < other.outcome.value
                and str(self.PolicyCls) < str(other.PolicyCls)
            )
        else:
            return NotImplemented
