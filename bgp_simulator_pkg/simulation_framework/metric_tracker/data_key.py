from dataclasses import dataclass
from typing import Union

from .metric_key import MetricKey

from bgp_simulator_pkg.enums import SpecialPercentAdoptions
from bgp_simulator_pkg.simulation_framework.scenarios import ScenarioConfig


@dataclass(frozen=True, slots=True)
class DataKey:
    """Key for storing data within the MetricTracker"""

    propagation_round: int
    percent_adopt: Union[float, SpecialPercentAdoptions]
    scenario_config: ScenarioConfig
    metric_key: MetricKey
