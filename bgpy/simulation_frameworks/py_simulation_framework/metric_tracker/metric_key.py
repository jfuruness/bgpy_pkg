from dataclasses import dataclass
from typing import Any, Optional, Union

from bgpy.enums import ASGroups, Plane, PyOutcomes, CPPOutcomes
from bgpy.simulation_engines.base import Policy


@dataclass(frozen=True, slots=True)
class MetricKey:
    """Key for storing data within each metric"""

    plane: Plane
    as_group: ASGroups
    outcome: CPPOutcomes | PyOutcomes
    PolicyCls: Union[Optional[type[Policy]], Any] = None
