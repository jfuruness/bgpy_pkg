from dataclasses import dataclass
from typing import Any

from bgpy.enums import ASGroups, Plane, Outcomes


@dataclass(frozen=True, slots=True)
class GraphCategory:
    """Properties for the type of graph you want"""

    plane: Plane
    as_group: ASGroups
    outcome: Outcomes
    in_adopting_asns: bool | type[Any]
