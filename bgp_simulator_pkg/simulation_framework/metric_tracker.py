from abc import ABC
from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Dict, List, Optional, Type, Union

import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

from .line import Line
from ...enums import ASTypes
from ...enums import Outcomes
from ...enums import SpecialPercentAdoptions
from ...simulation_engine import SimulationEngine
from ..scenarios import Scenario
from ...simulation_engine.announcement import Announcement as Ann

from caida_collector_pkg import AS


# Must be module level in order to be picklable
# https://stackoverflow.com/a/16439720/8903959
def default_dict_inner_func():
    return defaultdict(list)


def default_dict_func():
    return defaultdict(default_dict_inner_func)

class MetricTracker:
    """Tracks metrics used in graphs across trials"""

    def __init__(self):
        """Inits data"""

        # This is a list of all the trial info
        # You must save info trial by trial, so that you can join
        # After a return from multiprocessing
        # {propagation_round: {percent_adopt: [Metrics]}}
        self.data: DefaultDict[int,
                               DefaultDict[float,
                                           DefaultDict[
                                               Union[str,
                                                     SpecialPercentAdoptions],
                                               List[float]]]] =\
            defaultdict(default_dict_func)

    def add_trial_info(self, other_metric_tracker: "MetricTracker"):
        """Merges other MetricTracker into this one and combines the data

        NOTE this should probably use a dunder method, not this

        This gets called when we need to merge all the
        from the various processes that were spawned
        """

        raise NotImplementedError("Account for new structure")
        for prop_round, scenario_dict in other_subgraph.data.items():
            for scenario_label, percent_dict in scenario_dict.items():
                for percent_adopt, trial_results in percent_dict.items():
                    if isinstance(percent_adopt, SpecialPercentAdoptions):
                        percent_adopt = percent_adopt.value
                    self.data[prop_round][scenario_label][percent_adopt
                        ].extend(trial_results)  # noqa

    def track_trial_metrics(
        self,
        *,
        engine: SimulationEngine,
        percent_adopt: float,
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        outcomes: dict[str, dict[AS, Any]],
    ) -> None:
        """Tracks all metrics from a single trial, adding to self.data"""

        self._track_trial_metrics(
            engine=engine,
            percent_adopt=percent_adopt,
            trial=trial,
            scenario=scenario,
            propagation_round=propagation_round,
            outcomes=outcomes,
        )
        self._track_trial_metrics_hook(
            engine=engine,
            percent_adopt=percent_adopt,
            trial=trial,
            scenario=scenario,
            propagation_round=propagation_round,
            outcomes=outcomes,
        )

    def _track_trial_metrics(
        self,
        *,
        engine: SimulationEngine,
        percent_adopt: float,
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        outcomes=outcomes,
    ) -> None:
        """Tracks all metrics from a single trial, adding to self.data

        TODO: This should really be cleaned up, but good enough for now
        """


        raise NotImplementedError

    def _track_trial_metrics_hook(
        self,
        *,
        engine: SimulationEngine,
        percent_adopt: float,
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        outcomes=outcomes,
    ) -> None:
        """Hook function for easy subclassing by a user"""

        pass
