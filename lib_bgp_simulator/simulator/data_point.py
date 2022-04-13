from dataclasses import dataclass

from ..engine import BGPAS


@dataclass(frozen=True)
class DataPoint:
    """Data point in a graph"""

    percent_adoption: float
    GraphLabel: str
    propagation_round: int
