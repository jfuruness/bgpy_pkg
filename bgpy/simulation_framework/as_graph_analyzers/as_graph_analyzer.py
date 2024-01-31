from typing import Optional, TYPE_CHECKING

from bgpy.as_graphs import AS
from bgpy.enums import Plane, Outcomes, Relationships
from bgpy.simulation_engine import BaseSimulationEngine


from .base_as_graph_analyzer import BaseASGraphAnalyzer


if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_framework.scenarios import Scenario


class ASGraphAnalyzer(BaseASGraphAnalyzer):
    """Takes in a BaseSimulationEngine and outputs metrics"""

    def __init__(
        self,
        engine: BaseSimulationEngine,
        scenario: "Scenario",
        data_plane_tracking: bool = True,
        control_plane_tracking: bool = False,
    ) -> None:
        self.engine: BaseSimulationEngine = engine
        self.scenario: "Scenario" = scenario
        self._most_specific_ann_dict: dict[AS, Optional["Ann"]] = {
            # Get the most specific ann in the rib
            as_obj: self._get_most_specific_ann(as_obj)
            for as_obj in engine.as_graph
        }
        self._data_plane_outcomes: dict[int, int] = dict()
        self._control_plane_outcomes: dict[int, int] = dict()
        self.outcomes: dict[int, dict[int, int]] = {
            Plane.DATA.value: self._data_plane_outcomes,
            Plane.CTRL.value: self._control_plane_outcomes,
        }
        self.data_plane_tracking: bool = data_plane_tracking
        self.control_plane_tracking: bool = control_plane_tracking

    def _get_most_specific_ann(self, as_obj: AS) -> Optional["Ann"]:
        """Returns the most specific announcement that exists in a rib

        as_obj is the as
        ordered prefixes are prefixes ordered from most specific to least
        """

        for prefix in self.scenario.ordered_prefix_subprefix_dict:
            most_specific_ann = as_obj.policy._local_rib.get(prefix)
            if most_specific_ann:
                # Mypy doesn't recognize that this is always an annoucnement
                return most_specific_ann  # type: ignore
        return None

    def analyze(self) -> dict[int, dict[int, int]]:
        """Takes in engine and outputs traceback for ctrl + data plane data"""

        for as_obj in self.engine.as_graph:
            if self.data_plane_tracking:
                # Gets AS outcome and stores it in the outcomes dict
                self._get_as_outcome_data_plane(as_obj)
            if self.control_plane_tracking:
                self._get_as_outcome_ctrl_plane(as_obj)
            self._get_other_as_outcome_hook(as_obj)
        return self.outcomes

    ####################
    # Data plane funcs #
    ####################

    def _get_as_outcome_data_plane(self, as_obj: AS) -> int:
        """Recursively returns the as outcome"""

        if as_obj.asn in self._data_plane_outcomes:
            return self._data_plane_outcomes[as_obj.asn]
        else:
            most_specific_ann = self._most_specific_ann_dict[as_obj]
            outcome_int = self._determine_as_outcome_data_plane(
                as_obj, most_specific_ann
            )
            # We haven't traced back all the way on the AS path
            if outcome_int == Outcomes.UNDETERMINED.value:
                # next as in the AS path to traceback to
                # Ignore type because only way for this to be here
                # Is if the most specific "Ann" was NOT None.
                next_as = self.engine.as_graph.as_dict[
                    # NOTE: Starting in v4, this is the next hop,
                    # not the next ASN in the AS PATH
                    # This is more in line with real BGP and allows for more
                    # advanced types of hijacks such as origin spoofing hijacks
                    most_specific_ann.next_hop_asn  # type: ignore
                ]  # type: ignore
                outcome_int = self._get_as_outcome_data_plane(next_as)
            assert outcome_int != Outcomes.UNDETERMINED.value, "Shouldn't be possible"

            self._data_plane_outcomes[as_obj.asn] = outcome_int
            return outcome_int

    def _determine_as_outcome_data_plane(
        self, as_obj: AS, most_specific_ann: Optional["Ann"]
    ) -> int:
        """Determines the outcome at an AS

        ann is most_specific_ann is the most specific prefix announcement
        that exists at that AS
        """

        if as_obj.asn in self.scenario.attacker_asns:
            return Outcomes.ATTACKER_SUCCESS.value
        elif as_obj.asn in self.scenario.victim_asns:
            return Outcomes.VICTIM_SUCCESS.value
        # End of traceback
        elif (
            most_specific_ann is None  # type: ignore
            or len(most_specific_ann.as_path) == 1
            or most_specific_ann.recv_relationship.value == Relationships.ORIGIN.value
            or getattr(most_specific_ann, "traceback_end", False)
            # Adding this condition in V4 for proper next_hop behavior
            or most_specific_ann.next_hop_asn == as_obj.asn
        ):
            return Outcomes.DISCONNECTED.value
        else:
            return Outcomes.UNDETERMINED.value  # type: ignore

    #######################
    # Control Plane Funcs #
    #######################

    def _get_as_outcome_ctrl_plane(self, as_obj: AS) -> int:
        """Stores and returns the AS outcome from the control plane"""

        most_specific_ann = self._most_specific_ann_dict[as_obj]
        outcome_int = self._determine_as_outcome_ctrl_plane(as_obj, most_specific_ann)
        assert outcome_int != Outcomes.UNDETERMINED.value, "Shouldn't be possible"
        self._control_plane_outcomes[as_obj.asn] = outcome_int
        return outcome_int

    def _determine_as_outcome_ctrl_plane(self, as_obj: AS, ann: Optional["Ann"]) -> int:
        """Determines the outcome at an AS on the control plane

        ann is most_specific_ann is the most specific prefix announcement
        that exists at that AS
        """

        if not ann:
            return Outcomes.DISCONNECTED.value
        elif ann.origin in self.scenario.attacker_asns:
            return Outcomes.ATTACKER_SUCCESS.value
        elif ann.origin in self.scenario.victim_asns:
            return Outcomes.VICTIM_SUCCESS.value
        else:
            return Outcomes.DISCONNECTED.value

    ################################
    # Hook funcs for other metrics #
    ################################

    def _get_other_as_outcome_hook(self, as_obj: AS) -> int:
        # Noop, this is just to satisfy mypy
        return Outcomes.ATTACKER_SUCCESS.value
