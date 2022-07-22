from math import sqrt
from statistics import mean
from statistics import stdev


class Line:
    """Formats raw data for matplotlib graph"""

    def __init__(self, scenario_label: str, percent_adopt_dict: dict):
        """Stores info aobut a line in a graph"""

        # {percent_adopt: [percentages]}
        self.percent_adopt_dict: dict = percent_adopt_dict
        self.label: str = scenario_label
        self.xs: list[float] = self._get_xs()
        self.ys: list[float] = self._get_ys()
        self.yerrs: list[float] = self._get_yerrs()

    def _get_xs(self) -> list[float]:
        """"Gets X axis makers"""

        return list(self.percent_adopt_dict)

    def _get_ys(self) -> list[float]:
        """Gets Y axis markers"""

        return [mean(x) for x in self.percent_adopt_dict.values()]

    def _get_yerrs(self) -> list[float]:
        """Gets Yerr for each data point"""

        return [self._get_yerr(x) for x in self.percent_adopt_dict.values()]

    def _get_yerr(self, list_of_vals) -> float:
        """Gets yerr for a single list of values, 90% confidence"""

        if len(list_of_vals) > 1:
            yerr_num = 1.645 * 2 * stdev(list_of_vals)
            yerr_denom = sqrt(len(list_of_vals))
            return yerr_num / yerr_denom
        else:
            return 0
