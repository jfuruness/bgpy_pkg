from math import sqrt
from statistics import mean
from statistics import stdev
from typing import Union

from ...enums import SpecialPercentAdoptions


class DataAttackerSuccessAllLine(Line):
    """Graph line that tracks a metric"""

    def record_trial_info(
        self,
        percent_adopt: Union[float, SpecialPercentAdoption],
        engine: SimulationEngine,
        outcomes: dict[str, dict[AS, Any]],
    ) -> None:
        """Records trial info after a simulation run"""

        # Get the data plane outcomes
        data_plane_outcomes = outcomes[Plane.DATA.value]

        total_attacker_success = 0
        for as_ in engine:
            if outcomes[as_] == Outcomes.ATTACKER_SUCCESS:
                total_attacker_success += 1
        self.info[percent_adopt].append(total_attacker_success / len(engine))
