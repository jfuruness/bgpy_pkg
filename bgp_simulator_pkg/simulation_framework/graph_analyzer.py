from abc import ABC
from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Optional, Union

import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

from .line import Line
from ...enums import ASGroups
from ...enums import Outcomes
from ...enums import SpecialPercentAdoptions
from ...simulation_engine import SimulationEngine
from ..scenarios import Scenario
from ...simulation_engine.announcement import Announcement as Ann

from bgp_simulator_pkg.caida_collector import AS


class GraphAnalyzer:
    """Takes in a SimulationEngine and outputs metrics"""

    def __init__(self, engine: SimulationEngine, scenario: Scenario):
        self.engine: SimulationEngine = engine
        self.scenario: Scenario = scenario
        self.outcomes: dict[AS, dict[str, Any]] = dict()

    def analyze(self) -> dict[Any, Any]:
        """Takes in engine and outputs traceback for ctrl + data plane data"""

        raise NotImplementedError("put all data plane stuff in the data plane")

        for as_obj in engine:
            # Gets AS outcome and stores it in the outcomes dict
            self._get_as_data_plane_outcome(as_obj)
        raise NotImplementedError("Get ctrl plane outcomes here")
        raise NotImplementedError("Get other outcomes hook here (no op)")
        return outcomes

    def _get_as_outcome(self, as_obj: AS) -> Outcomes:
        """Recursively returns the as outcome"""

        if as_obj in outcomes:
            return outcomes[as_obj]
        else:
            # Get the most specific announcement in the rib
            most_specific_ann = self._get_most_specific_ann(as_obj)
            raise NotImplementedError("Move this out of the scenario cls")
            # This has to be done in the scenario
            # Because only the scenario knows attacker/victim
            # And it's possible for scenario's to have multiple attackers
            # or multiple victims or different ways of determining outcomes
            outcome = scenario.determine_as_outcome(as_obj, most_specific_ann)
            # We haven't traced back all the way on the AS path
            if outcome == Outcomes.UNDETERMINED:
                # next as in the AS path to traceback to
                # Ignore type because only way for this to be here
                # Is if the most specific Ann was NOT None.
                next_as = engine.as_dict[
                    most_specific_ann.as_path[1]  # type: ignore
                ]  # type: ignore
                outcome = self._get_as_outcome(next_as, outcomes, engine, scenario)
            assert outcome != Outcomes.UNDETERMINED, "Shouldn't be possible"

            outcomes[as_obj] = outcome
            assert isinstance(outcome, Outcomes), "For mypy"
            return outcome

    def _get_most_specific_ann(self, as_obj) -> Optional[Ann]:
        """Returns the most specific announcement that exists in a rib

        as_obj is the as
        ordered prefixes are prefixes ordered from most specific to least
        """

        for prefix in self.scenario.ordered_prefix_subprefix_dict:
            most_specific_ann = as_obj._local_rib.get_ann(prefix)
            if most_specific_ann:
                # Mypy doesn't recognize that this is always an annoucnement
                return most_specific_ann  # type: ignore
        return None

    def _determine_as_outcome(
        self,
        as_obj: AS,
        most_specific_ann: Optional[Announcement]
    ) -> Outcomes:
        """Determines the outcome at an AS

        ann is most_specific_ann is the most specific prefix announcement
        that exists at that AS
        """

        if as_obj.asn in self.attacker_asns:
            return Outcomes.ATTACKER_SUCCESS
        elif as_obj.asn in self.victim_asns:
            return Outcomes.VICTIM_SUCCESS
        # End of traceback
        elif (
            ann is None
            or len(ann.as_path) == 1
            or ann.recv_relationship == Relationships.ORIGIN
            or ann.traceback_end
        ):
            return Outcomes.DISCONNECTED
        else:
            return Outcomes.UNDETERMINED

    def determine_as_outcome_ctrl_plane(
        self, as_obj: AS, ann: Optional[Announcement]
    ) -> Outcomes:
        """Determines the outcome at an AS on the control plane

        ann is most_specific_ann is the most specific prefix announcement
        that exists at that AS
        """

        if not ann:
            return Outcomes.DISCONNECTED
        elif ann.origin in self.attacker_asns:
            return Outcomes.ATTACKER_SUCCESS
        elif ann.origin in self.victim_asns:
            return Outcomes.VICTIM_SUCCESS
        else:
            return Outcomes.DISCONNECTED

