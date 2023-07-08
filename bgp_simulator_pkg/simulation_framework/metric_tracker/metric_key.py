from dataclasses import dataclass
from typing import Union

from .metric import Metric

from bgp_simulator_pkg.enums import Plane, ASGroup, Outcome
from bgp_simulator_pkg.simulation_engine import AS


@dataclass(frozen=True, slots=True)
class MetricKey:
    """Key for storing data within each metric"""

    plane: Plane
    as_group: ASGroup
    outcome: Outcome
    ASCls: Optional[type[AS]] = None
