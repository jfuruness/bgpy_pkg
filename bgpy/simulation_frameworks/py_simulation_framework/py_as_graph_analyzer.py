from typing import Any, Optional, TYPE_CHECKING, Union

from bgpy.as_graphs import AS
from bgpy.enums import Plane, CPPOutcomes, PyOutcomes, PyRelationships
from bgpy.simulation_engines.base import SimulationEngine
from bgpy.simulation_frameworks.base import ASGraphAnalyzer

from .scenarios import Scenario

if TYPE_CHECKING:

    from bgpy.simulation_engines.py_simulation_engine import PyAnnouncement as PyAnn
    from bgpy.simulation_engines.cpp_simulation_engine import CPPAnnouncement as CPPAnn


class PyASGraphAnalyzer(ASGraphAnalyzer):
    """Takes in a SimulationEngine and outputs metrics"""

    def __init__(self, engine: SimulationEngine, scenario: Scenario):
        self.engine: SimulationEngine = engine
        self.scenario: Scenario = scenario
        self._most_specific_ann_dict: dict[AS, Optional[Union["PyAnn", "CPPAnn"]]] = {
            # Get the most specific ann in the rib
            as_obj: self._get_most_specific_ann(as_obj)
            for as_obj in engine.as_graph
        }
        self._data_plane_outcomes: dict[
            int, Union["CPPOutcomes", "PyOutcomes"]
        ] = dict()
        self._control_plane_outcomes: dict[
            int, Union["CPPOutcomes", "PyOutcomes"]
        ] = dict()
        self.outcomes: dict[int, dict[int, Any]] = {
            Plane.DATA.value: self._data_plane_outcomes,
            Plane.CTRL.value: self._control_plane_outcomes,
        }

    def _get_most_specific_ann(self, as_obj: AS) -> Optional[Union["PyAnn", "CPPAnn"]]:
        """Returns the most specific announcement that exists in a rib

        as_obj is the as
        ordered prefixes are prefixes ordered from most specific to least
        """

        for prefix in self.scenario.ordered_prefix_subprefix_dict:
            most_specific_ann = as_obj.policy._local_rib.get_ann(prefix)
            if most_specific_ann:
                # Mypy doesn't recognize that this is always an annoucnement
                return most_specific_ann  # type: ignore
        return None

    def analyze(self) -> dict[int, dict[int, Union["CPPOutcomes", "PyOutcomes"]]]:
        """Takes in engine and outputs traceback for ctrl + data plane data"""

        for as_obj in self.engine.as_graph:
            # Gets AS outcome and stores it in the outcomes dict
            self._get_as_outcome_data_plane(as_obj)
            self._get_as_outcome_ctrl_plane(as_obj)
            self._get_other_as_outcome_hook(as_obj)
        return self.outcomes

    ####################
    # Data plane funcs #
    ####################

    def _get_as_outcome_data_plane(
        self, as_obj: AS
    ) -> Union["CPPOutcomes", "PyOutcomes"]:
        """Recursively returns the as outcome"""

        if as_obj in self._data_plane_outcomes:
            return self._data_plane_outcomes[as_obj.asn]
        else:
            most_specific_ann = self._most_specific_ann_dict[as_obj]
            outcome = self._determine_as_outcome_data_plane(as_obj, most_specific_ann)
            # We haven't traced back all the way on the AS path
            if outcome == PyOutcomes.UNDETERMINED:
                # next as in the AS path to traceback to
                # Ignore type because only way for this to be here
                # Is if the most specific Ann was NOT None.
                next_as = self.engine.as_graph.as_dict[
                    most_specific_ann.as_path[1]  # type: ignore
                ]  # type: ignore
                outcome = self._get_as_outcome_data_plane(next_as)
            assert outcome != PyOutcomes.UNDETERMINED, "Shouldn't be possible"

            self._data_plane_outcomes[as_obj.asn] = outcome
            assert isinstance(outcome, (CPPOutcomes, PyOutcomes)), "For mypy"
            return outcome

    def _determine_as_outcome_data_plane(
        self, as_obj: AS, most_specific_ann: Optional[Union["PyAnn", "CPPAnn"]]
    ) -> Union["CPPOutcomes", "PyOutcomes"]:
        """Determines the outcome at an AS

        ann is most_specific_ann is the most specific prefix announcement
        that exists at that AS
        """

        if as_obj.asn in self.scenario.attacker_asns:
            return PyOutcomes.ATTACKER_SUCCESS
        elif as_obj.asn in self.scenario.victim_asns:
            return PyOutcomes.VICTIM_SUCCESS
        # End of traceback
        elif (
            most_specific_ann is None
            or len(most_specific_ann.as_path) == 1
            or most_specific_ann.recv_relationship.value == PyRelationships.ORIGIN.value
            or most_specific_ann.traceback_end
        ):
            return PyOutcomes.DISCONNECTED
        else:
            return PyOutcomes.UNDETERMINED

    #######################
    # Control Plane Funcs #
    #######################

    def _get_as_outcome_ctrl_plane(
        self, as_obj: AS
    ) -> Union["CPPOutcomes", "PyOutcomes"]:
        """Stores and returns the AS outcome from the control plane"""

        most_specific_ann = self._most_specific_ann_dict[as_obj]
        outcome = self._determine_as_outcome_ctrl_plane(as_obj, most_specific_ann)
        assert outcome != PyOutcomes.UNDETERMINED, "Shouldn't be possible"
        self._control_plane_outcomes[as_obj.asn] = outcome
        assert isinstance(outcome, (CPPOutcomes, PyOutcomes)), "For mypy"
        return outcome

    def _determine_as_outcome_ctrl_plane(
        self, as_obj: AS, ann: Optional[Union["PyAnn", "CPPAnn"]]
    ) -> Union["CPPOutcomes", "PyOutcomes"]:
        """Determines the outcome at an AS on the control plane

        ann is most_specific_ann is the most specific prefix announcement
        that exists at that AS
        """

        if not ann:
            return PyOutcomes.DISCONNECTED
        elif ann.origin in self.scenario.attacker_asns:
            return PyOutcomes.ATTACKER_SUCCESS
        elif ann.origin in self.scenario.victim_asns:
            return PyOutcomes.VICTIM_SUCCESS
        else:
            return PyOutcomes.DISCONNECTED

    ################################
    # Hook funcs for other metrics #
    ################################

    def _get_other_as_outcome_hook(
        self, as_obj: AS
    ) -> Union["CPPOutcomes", "PyOutcomes"]:
        # Noop, this is just to satisfy mypy
        return PyOutcomes.ATTACKER_SUCCESS
