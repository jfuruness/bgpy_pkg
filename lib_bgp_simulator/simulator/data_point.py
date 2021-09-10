from dataclasses import dataclass

from ..engine.bgp_policy import BGPPolicy

@dataclass(frozen=True)
class DataPoint:
    """Data point in a graph"""

    percent_adoption: float
    PolicyCls: BGPPolicy
    propagation_round: int
