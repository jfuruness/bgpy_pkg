from collections import defaultdict
from typing import Optional, Union

from bgp_simulator_pkg.caida_collector.graph.base_as import AS
from bgp_simulator_pkg.enums import Outcomes
from bgp_simulator_pkg.simulation_engine import SimulationEngine
from bgp_simulator_pkg.simulation_framework.scenarios import Scenario


class Metric:
    """Tracks a single metric"""

    def __init__(
        self,
        percents: Optional[defaultdict[str, list[float]]] = None,
    ) -> None:
        self._numerators: defaultdict[type[AS], float] = defaultdict(float)
        self._denominators: defaultdict[type[AS], float] = defaultdict(float)
        if percents:
            self.percents:  defaultdict[str, list[float]] = percents
        else:
            self.percents = defaultdict(list)

    def __add__(self, other) -> Union["Metric", type[NotImplemented]]:
        """Adds metric classes together"""

        if isinstance(other, Metric):
            agg_percents = self.percents.copy()
            for as_cls, percent_list in other.percents.items():
                agg_percents[as_cls].extend(percent_list)
            return Metric(percents=agg_percents)
        else:
            return NotImplemented

    def save_percents(self) -> None:
        """Returns percentages to be added to all metrics"""

        percents = defaultdict(list)
        for (as_cls, numerator), (_, denominator) in zip(
            self._numerators.items(),
            self._denominators.items()
        ):
            k = f"{self.label_prefix}_{as_cls.__name__}"
            percents[k] = [100 * numerator / denominator]
        self.percents = percents

    def add_data(
        self,
        *,
        as_obj: AS,
        engine: SimulationEngine,
        scenario: Scenario,
        ctrl_plane_outcome: Outcomes,
        data_plane_outcome: Outcomes,
    ):

        within_denom = self._add_denominator(
            as_obj=as_obj,
            engine=engine,
            scenario=scenario,
            ctrl_plane_outcome=ctrl_plane_outcome,
            data_plane_outcome=data_plane_outcome,
        )

        if within_denom:
            self._add_numerator(
                as_obj=as_obj,
                engine=engine,
                scenario=scenario,
                ctrl_plane_outcome=ctrl_plane_outcome,
                data_plane_outcome=data_plane_outcome,
            )

    def _add_numerator(
        self,
        *,
        as_obj: AS,
        engine: SimulationEngine,
        scenario: Scenario,
        ctrl_plane_outcome: Outcomes,
        data_plane_outcome: Outcomes,
    ) -> None:
        raise NotImplementedError

    def _add_denominator(
        self,
        *,
        as_obj: AS,
        engine: SimulationEngine,
        scenario: Scenario,
        ctrl_plane_outcome: Outcomes,
        data_plane_outcome: Outcomes,
    ) -> bool:
        raise NotImplementedError

    @property
    def label_prefix(self) -> str:
        raise NotImplementedError
