from dataclasses import dataclass

from bgpy.shared.enums import SpecialPercentAdoptions
from bgpy.simulation_framework.scenarios import ScenarioConfig


@dataclass(frozen=True, slots=True)
class DataPointKey:
    """Key for the data stored in a single point in a graph"""

    propagation_round: int
    percent_adopt: float | SpecialPercentAdoptions
    scenario_config: ScenarioConfig
