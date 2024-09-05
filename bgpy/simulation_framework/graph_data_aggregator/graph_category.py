from dataclasses import dataclass
from typing import Any

from bgpy.shared.enums import ASGroups, Outcomes, Plane, InAdoptingASNs


@dataclass(frozen=True, slots=True)
class GraphCategory:
    """Properties for the type of graph you want"""

    plane: Plane
    as_group: ASGroups
    outcome: Outcomes
    in_adopting_asns: InAdoptingASNs
