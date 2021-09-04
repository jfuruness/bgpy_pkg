from dataclasses import dataclass

from lib_caida_collector import AS

@dataclass(frozen=True)
class DataPoint:
    """Data point in a graph"""

    percent_adoption: float
    ASCls: AS
    propagation_round: int
