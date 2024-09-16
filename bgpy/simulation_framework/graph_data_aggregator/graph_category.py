from dataclasses import dataclass

from bgpy.shared.enums import ASGroups, InAdoptingASNs, Outcomes, Plane


@dataclass(frozen=True, slots=True)
class GraphCategory:
    """Properties for the type of graph you want"""

    plane: Plane
    as_group: ASGroups
    outcome: Outcomes
    in_adopting_asns: InAdoptingASNs
