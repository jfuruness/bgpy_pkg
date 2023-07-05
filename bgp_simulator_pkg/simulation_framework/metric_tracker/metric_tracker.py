from abc import ABC
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, DefaultDict, Dict, List, Optional, Type, Union

import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

from .line import Line
from .metric import Metric
from ...enums import ASTypes
from ...enums import Outcomes
from ...enums import SpecialPercentAdoptions
from ...simulation_engine import SimulationEngine
from ..scenarios import Scenario
from ...simulation_engine.announcement import Announcement as Ann

from bgp_simulator_pkg.caida_collector.graph.base_as import AS


class MetricTracker:
    """Tracks metrics used in graphs across trials"""

    def __init__(self, default_data: Optional[defaultdict[DataKey, list[Metric]]] = None):
        """Inits data"""

        # This is a list of all the trial info
        # You must save info trial by trial, so that you can join
        # After a return from multiprocessing
        # key DataKey (prop_round, percent_adopt, scenario_label, MetricCls)
        # value is a list of metric instances
        if default_data:
            self.data: defaultdict[DataKey, list[Metric]] = defaultdata
        else:
            self.data = defaultdict(list)

    def __add__(self, other):
        """Merges other MetricTracker into this one and combines the data

        This gets called when we need to merge all the MetricTrackers
        from the various processes that were spawned
        """

        if isinstance(other, MetricTracker):
            new_data: defaultdict[DataKey, list[Metric]] = deepcopy(self.data)
            for k, v in other.data.items():
                new_data[k].extend(v)
            return MetricTracker(default_data=new_data)
        else:
            return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

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
        """Tracks all metrics from a single trial, adding to self.data

        The reason we don't simply save the engine to track metrics later
        is because the engines are very large and this would take a lot longer
        """

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
            key = DataKey(
                propagation_round=propagation_round,
                percent_adopt=percent_adopt,
                scenario_label=scenario.unique_data_label,
                MetricCls=metric.__class__,
            )
            self.data[key].append(metric)

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
