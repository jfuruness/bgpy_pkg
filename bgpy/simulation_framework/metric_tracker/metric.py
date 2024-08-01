from collections import defaultdict
from dataclasses import replace
from typing import Optional, Type

from bgpy.enums import Plane
from bgpy.as_graphs import AS
from bgpy.simulation_engine import Policy, BaseSimulationEngine
from bgpy.simulation_framework.scenarios import Scenario

from .metric_key import MetricKey


class Metric:
    """Tracks a single metric"""

    def __init__(
        self,
        metric_key: MetricKey,
    ) -> None:
        # At this point the PolicyCls is None for the metric_key,
        # it's later added in the save_percents
        self.metric_key: MetricKey = metric_key
        self._numerator: float = 0
        self._denominator: float = 0

    def get_percent(self) -> Optional[float]:
        if self._numerator == 0 and self._denominator == 0:
            return None
        else:
            return self._numerator / self._denominator

    def add_data(
        self,
        *,
        as_obj: AS,
        engine: BaseSimulationEngine,
        scenario: Scenario,
        ctrl_plane_outcome: int,
        data_plane_outcome: int,
    ):

        within_denom =  self._add_denominator(
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

    def _add_denominator(
        self,
        *,
        as_obj: AS,
        engine: BaseSimulationEngine,
        scenario: Scenario,
        ctrl_plane_outcome: int,
        data_plane_outcome: int,
    ) -> bool:
        """Adds to the denominator if it is within the as group and adopting"""

        if as_obj.asn in engine.as_graph.asn_groups[self.metric_key.as_group.value]:

            adopting = as_obj.asn in scenario.adopting_asns
            if self.metric_key.in_adopting_asns is Any:
                self._denominator += 1
                return True
            else:
                adopting = as_obj.asn in scenario.adopting_asns
                if adopting:
                    self._denominator += 1
                    return True
        return False

    def _add_numerator(
        self,
        *,
        as_obj: AS,
        engine: BaseSimulationEngine,
        scenario: Scenario,
        ctrl_plane_outcome: int,
        data_plane_outcome: int,
    ) -> None:
        """Adds to numerator if it is within denom and outcome is correct

        NOTE: This should only be called if _add_denominator returns True
        """

        if self.metric_key.plane == Plane.DATA:
            outcome = data_plane_outcome
        elif self.metric_key.plane == Plane.CTRL:
            outcome = ctrl_plane_outcome
        else:
            raise NotImplementedError

        # NOTE: no need to check the group again, we already checked it
        # in the add denominator func
        if outcome == self.metric_key.outcome.value:
            self._numerator += 1
