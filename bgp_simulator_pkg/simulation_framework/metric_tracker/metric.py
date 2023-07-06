from abc import ABC, abstractmethod
from collections import defaultdict

from bgp_simulator_pkg.caida_collector.graph.base_as import AS
from bgp_simulator_pkg.enums import Outcomes
from bgp_simulator_pkg.simulation_engine import SimulationEngine
from bgp_simulator_pkg.simulation_framework.scenarios import Scenario


class Metric(ABC):
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

    def __add__(self, other) -> Union["Metric", NotImplemented]:
        """Adds metric classes together"""

        if isinstance(other, Metric):
            agg_percents = self.percents.copy()
            for as_cls, percent_list in other.get_percents():
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

        self._add_numerator(
            as_obj=as_obj,
            engine=engine,
            scenario=scenario,
            ctrl_plane_outcome=ctrl_plane_outcome,
            data_plane_outcome=data_plane_outcome,
        )

        self._add_denominator(
            as_obj=as_obj,
            engine=engine,
            scenario=scenario,
            ctrl_plane_outcome=ctrl_plane_outcome,
            data_plane_outcome=data_plane_outcome,
        )
        self.save_percents()

    @abstractmethod
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

    @abstractmethod
    def _add_denominator(
        self,
        *,
        as_obj: AS,
        engine: SimulationEngine,
        scenario: Scenario,
        ctrl_plane_outcome: Outcomes,
        data_plane_outcome: Outcomes,
    ) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def label_prefix(self) -> str:
        raise NotImplementedError
