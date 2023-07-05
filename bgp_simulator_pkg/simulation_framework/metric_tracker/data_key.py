from dataclasses import dataclass

from .metric import Metric


@dataclass(frozen=True)
class DataKey:
    """Key for storing data within the MetricTracker"""

    propagation_round: int
    percent_adopt: float
    scenario_label: str
    MetricCls: type[Metric]
