from dataclasses import dataclass
from typing import Optional

from bgp_simulator_pkg.enums import ASGroups, Plane, Outcomes
from bgp_simulator_pkg.caida_collector.graph.base_as import AS


@dataclass(frozen=True, slots=True)
class MetricKey:
    """Key for storing data within each metric"""

    plane: Plane
    as_group: ASGroups
    outcome: Outcomes
    ASCls: Optional[type[AS]] = None
