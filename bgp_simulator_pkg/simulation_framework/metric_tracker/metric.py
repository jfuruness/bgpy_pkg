from collections import defaultdict
from dataclasses import replace
from typing import Optional

from yamlable import YamlAble, yaml_info

from bgp_simulator_pkg.caida_collector.graph.base_as import AS
from bgp_simulator_pkg.enums import Plane, Outcomes
from bgp_simulator_pkg.simulation_engine import SimulationEngine
from bgp_simulator_pkg.simulation_framework.scenarios import Scenario

from .metric_key import MetricKey


@yaml_info(yaml_tag="Metric")
class Metric(YamlAble):
    """Tracks a single metric"""

    def __init__(
        self,
        metric_key: MetricKey,
        percents: Optional[defaultdict[str, list[float]]] = None,
    ) -> None:

        self.metric_key: MetricKey = metric_key
        self._numerators: defaultdict[type[AS], float] = defaultdict(float)
        self._denominators: defaultdict[type[AS], float] = defaultdict(float)
        if percents:
            self.percents: defaultdict[MetricKey, list[float]] = percents
        else:
            self.percents = defaultdict(list)

    def __add__(self, other):
        """Adds metric classes together"""

        if isinstance(other, Metric):
            agg_percents = self.percents.copy()
            for metric_key, percent_list in other.percents.items():
                agg_percents[metric_key].extend(percent_list)
            return Metric(metric_key=self.metric_key, percents=agg_percents)
        else:
            return NotImplemented

    def save_percents(self) -> None:
        """Returns percentages to be added to all metrics"""

        percents = defaultdict(list)
        for (as_cls, numerator), (_, denominator) in zip(
            self._numerators.items(), self._denominators.items()
        ):
            k = replace(self.metric_key, ASCls=as_cls)
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
        """Adds to numerator if it is within the as group and the outcome is correct"""

        if self.metric_key.plane == Plane.DATA:
            outcome = data_plane_outcome
        elif self.metric_key.plane == Plane.CTRL:
            outcome = ctrl_plane_outcome
        else:
            raise NotImplementedError

        asn_group = engine.asn_groups[self.metric_key.as_group.value]
        if as_obj.asn in asn_group and outcome == self.metric_key.outcome:
            self._numerators[as_obj.__class__] += 1

    def _add_denominator(
        self,
        *,
        as_obj: AS,
        engine: SimulationEngine,
        scenario: Scenario,
        ctrl_plane_outcome: Outcomes,
        data_plane_outcome: Outcomes,
    ) -> bool:
        """Adds to the denominator if it is within the as group"""

        if as_obj.asn in engine.asn_groups[self.metric_key.as_group.value]:
            self._denominators[as_obj.__class__] += 1
            return True
        else:
            return False
