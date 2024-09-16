from bgpy.as_graphs import AS
from bgpy.shared.enums import InAdoptingASNs, Plane
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_framework.scenarios import Scenario

from .graph_category import GraphCategory


class TrialData:
    """Tracks trial data for a single graph category (for a single trial)"""

    def __init__(self, graph_category: GraphCategory) -> None:
        self.graph_category: GraphCategory = graph_category
        self._numerator: float = 0
        self._denominator: float = 0

    def get_percent(self) -> float | None:
        if self._numerator == 0 and self._denominator == 0:
            return None
        else:
            return self._numerator * 100 / self._denominator

    def add_data(
        self,
        *,
        as_obj: AS,
        engine: BaseSimulationEngine,
        scenario: Scenario,
        ctrl_plane_outcome: int,
        data_plane_outcome: int,
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

        if as_obj.asn in engine.as_graph.asn_groups[self.graph_category.as_group.value]:
            if self.graph_category.in_adopting_asns == InAdoptingASNs.ANY:
                self._denominator += 1
                return True
            else:
                in_adopting_asns = as_obj.asn in scenario.adopting_asns
                if (
                    self.graph_category.in_adopting_asns == InAdoptingASNs.TRUE
                    and in_adopting_asns
                ) or (
                    self.graph_category.in_adopting_asns == InAdoptingASNs.FALSE
                    and not in_adopting_asns
                ):
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

        if self.graph_category.plane == Plane.DATA:
            outcome = data_plane_outcome
        elif self.graph_category.plane == Plane.CTRL:
            outcome = ctrl_plane_outcome
        else:
            raise NotImplementedError

        # NOTE: no need to check the group again, we already checked it
        # in the add denominator func
        if outcome == self.graph_category.outcome.value:
            self._numerator += 1
