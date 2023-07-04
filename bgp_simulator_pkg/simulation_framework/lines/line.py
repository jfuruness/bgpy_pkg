from math import sqrt
from statistics import mean
from statistics import stdev
from typing import Union

from ...enums import SpecialPercentAdoptions


class Line(ABC):
    """Graph line that tracks a metric"""

    def __init__(
        self,
        label: str,
        percent_adopt_vals: list[Union[float, SpecialPercentAdoptions]]
    ) -> None:
        """Stores info aobut a line in a graph"""

        self.label: str = label
        self.percent_adopt_vals: list[Union[float, SpecialPercentAdoptions]]
        self.info: dict[Union[float, SpecialPercentAdoptions], list[float]] = {
            x: list() for x in self.percent_adopt_vals
        }

    @abstractmethod
    def record_trial_info(
        self,
        percent_adopt: Union[float, SpecialPercentAdoption],
        engine: SimulationEngine,
        outcomes: dict[str, dict[AS, Any]],
    ):
        """Records trial info after a simulation run"""

        raise NotImplementedError

    @property
    def xs(self) -> list[float]:
        """ "Gets X axis makers"""

        # Convert decimals to whole numbers
        return [x * 100 for x in self.percent_adopt_vals]

    @property
    def ys(self) -> list[float]:
        """Gets Y axis markers"""

        return [mean(trial_vals) for trial_vals in self.info.values()]

    @property
    def yerrs(self) -> list[float]:
        """Gets Yerr for each data point"""

        return [self._get_yerr(trial_vals) for trial_vals in self.info.values()]

    def _get_yerr(self, trial_vals: list[float]) -> float:
        """Gets yerr for a single list of values, 90% confidence"""

        if len(trial_vals) > 1:
            yerr_num = 1.645 * 2 * stdev(trial_vals)
            yerr_denom = sqrt(len(trial_vals))
            return float(yerr_num / yerr_denom)
        else:
            return 0
