from bgp_simulator_pkg.caida_collector.graph.base_as import AS


class Metric:
    """Tracks a single metric"""

    def __init__(self) -> None:
        self._numerators: defaultdict[type[AS], float] = defaultdict(float)
        self._demoninators: defaultdict[type[AS], float] = defaultdict(float)

    @property
    def percents(self) -> dict[str, float]:
        """Returns percentages to be added to all metrics"""

        percents = dict()
        for (as_cls, numerator), (_, denominator) in zip(
            self._numerators.items(),
            self._denominators.items()
        ):
            k = f"{self.label_prefix}_{as_cls.__name__}"
            percents[k] = 100 * numerator / denominator

        return percents

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
    @abstactmethod
    def label_prefix(self) -> str:
        raise NotImplementedError
