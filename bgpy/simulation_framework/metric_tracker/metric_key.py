from dataclasses import dataclass
from typing import Optional

from bgpy.enums import ASGroups, Plane, Outcomes
from bgpy.simulation_engine import BGPSimplePolicy


@dataclass(frozen=True, slots=True)
class MetricKey:
    """Key for storing data within each metric"""

    plane: Plane
    as_group: ASGroups
    outcome: Outcomes
    PolicyCls: Optional[type[BGPSimplePolicy]] = None
