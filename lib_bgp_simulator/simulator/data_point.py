from dataclasses import dataclass


@dataclass(frozen=True)
class DataPoint:
    """Data point in a graph"""

    percent_adoption: float
    ASCls: AS
    propagation_round: int
