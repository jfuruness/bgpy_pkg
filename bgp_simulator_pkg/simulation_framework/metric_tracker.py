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
        # {propagation_round: {percent_adopt: {Metric.__class__: [Metrics]}}}
        self.data: DefaultDict[int,
                               DefaultDict[Union[float, SpecialPercentAdoptions],
                                           DefaultDict[
                                               type[Metric],
                                               List[Metric]]]] =\
            defaultdict(default_dict_func)

    def add_trial_info(self, other_metric_tracker: "MetricTracker"):
        """Merges other MetricTracker into this one and combines the data

        NOTE this should probably use a dunder method, not this

        This gets called when we need to merge all the
        from the various processes that were spawned
        """

        for prop_round, outer_dict in other_metric_tracker.items():
            for percent_adopt, metric_dict in outer_dict.items():
                for MetricCls, metric_list in metric_dict.items():
                    self.data[prop_round][percent_adopt][MetricCls].extend(metric_list)

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


        metrics = self.metric_factory.get_metric_subclasses()
        self._populate_metrics(engine=engine, scenario=scenario, outcomes=outcomes)
        for metric in metrics:
            self.data[propagation_round][percent_adopt][metric.__class__].append(metric)

    def _populate_metrics(
        self,
        *,
        metrics: list[Metric],
        engine: SimulationEngine,
        scenario: Scenario,
        outcomes=outcomes,
    ) -> None:
        """Populates all metrics with data"""

        ctrl_plane_outcomes = outcomes[Plane.CTRL.value]
        data_plane_outcomes = outcomes[Plane.DATA.value]

        # Don't count these!
        uncountable_asns = scenario.preset_asns

        for as_obj in engine:
            # Don't count preset ASNs
            if as_obj.asn in uncountable_asns:
                continue
            for metric in metrics:
                metric.add_data(
                    as_obj=as_obj,
                    engine=engine,
                    scenario=scenario,
                    ctrl_plane_outcome=ctrl_plane_outcomes[as_obj]
                    data_plane_outcome=data_plane_outcomes[as_obj]
                )

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
