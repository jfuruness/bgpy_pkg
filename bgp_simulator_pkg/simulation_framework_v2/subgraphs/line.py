from math import sqrt
from statistics import mean
from statistics import stdev
from typing import Dict, List, Union

from ...enums import SpecialPercentAdoptions


class Line:
    """Formats raw data for matplotlib graph"""

    def __init__(
        self,
        scenario_label: str,
        percent_adopt_dict: Dict[Union[float, SpecialPercentAdoptions], List[float]],
    ) -> None:
        """Stores info aobut a line in a graph"""

        # {percent_adopt: [percentages]}
        self.percent_adopt_dict: Dict[float, List[float]] = dict()

        for k, v in percent_adopt_dict.items():
            key = k.value if isinstance(k, SpecialPercentAdoptions) else k
            self.percent_adopt_dict[key] = v

        self.percent_adopt_dict = {
            k: v for k, v in sorted(self.percent_adopt_dict.items())
        }

        # Remove the term Simple from the graphs
        self.label: str = scenario_label.replace("Simple", "")
        self.xs: List[float] = self._get_xs()
        self.ys: List[float] = self._get_ys()
        self.yerrs: List[float] = self._get_yerrs()

    def _get_xs(self) -> List[float]:
        """ "Gets X axis makers"""

        # Convert decimals to whole numbers
        return [x * 100 for x in self.percent_adopt_dict]

    def _get_ys(self) -> List[float]:
        """Gets Y axis markers"""

        return [mean(x) for x in self.percent_adopt_dict.values()]

    def _get_yerrs(self) -> List[float]:
        """Gets Yerr for each data point"""

        return [self._get_yerr(x) for x in self.percent_adopt_dict.values()]

    def _get_yerr(self, list_of_vals) -> float:
        """Gets yerr for a single list of values, 90% confidence"""

        if len(list_of_vals) > 1:
            yerr_num = 1.645 * 2 * stdev(list_of_vals)
            yerr_denom = sqrt(len(list_of_vals))
            return float(yerr_num / yerr_denom)
        else:
            return 0
