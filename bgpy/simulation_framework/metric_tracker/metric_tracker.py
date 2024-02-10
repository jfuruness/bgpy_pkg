from collections import defaultdict
import csv
from math import sqrt
from pathlib import Path
import pickle
from statistics import mean
from statistics import stdev
from typing import Any, Optional, Union

from .data_key import DataKey
from .metric import Metric
from .metric_key import MetricKey

from bgpy.enums import Plane, SpecialPercentAdoptions, Outcomes
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_framework.scenarios import Scenario
from bgpy.simulation_framework.utils import get_all_metric_keys


class MetricTracker:
    """Tracks metrics used in graphs across trials"""

    def __init__(
        self,
        data: Optional[defaultdict[DataKey, list[Metric]]] = None,
        metric_keys: tuple[MetricKey, ...] = tuple(list(get_all_metric_keys())),
    ):
        """Inits data"""

        # This is a list of all the trial info
        # You must save info trial by trial, so that you can join
        # After a return from multiprocessing
        # key DataKey (prop_round, percent_adopt, scenario_label, MetricKey)
        # value is a list of metric instances
        if data:
            self.data: defaultdict[DataKey, list[Metric]] = data
        else:
            self.data = defaultdict(list)

        self.metric_keys: tuple[MetricKey, ...] = metric_keys

    #############
    # Add Funcs #
    #############

    def __add__(self, other):
        """Merges other MetricTracker into this one and combines the data

        This gets called when we need to merge all the MetricTrackers
        from the various processes that were spawned
        """

        if isinstance(other, MetricTracker):
            # Deepcopy is slow, but fine here since it's only called once after sims
            # For BGPy __main__ using 100 trials, 3 percent adoptions, 1 scenario
            # on a lenovo laptop
            # 1.5s
            # new_data: defaultdict[DataKey, list[Metric]] = deepcopy(self.data)
            # .04s, but dangerous
            # new_data: defaultdict[DataKey, list[Metric]] = self.data
            # for k, v in other.data.items():
            #     new_data[k].extend(v)
            # .04s, not dangerous
            new_data: defaultdict[DataKey, list[Metric]] = defaultdict(list)
            for obj in (self, other):
                for k, v in obj.data.items():
                    new_data[k].extend(v)
            return self.__class__(data=new_data)
        else:
            return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    ######################
    # Data Writing Funcs #
    ######################

    def write_data(
        self,
        csv_path: Path,
        pickle_path: Path,
    ) -> None:
        """Writes data to CSV and pickles it"""

        with csv_path.open("w") as f:
            rows = self.get_csv_rows()
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        with pickle_path.open("wb") as f:
            pickle.dump(self.get_pickle_data(), f)

    def get_csv_rows(self) -> list[dict[str, Any]]:
        """Returns rows for a CSV"""

        rows = list()
        for data_key, metric_list in self.data.items():
            agg_percents = sum(metric_list, start=metric_list[0]).percents
            # useful for debugging individual trials
            # from pprint import pprint
            # pprint(data_key)
            # for x in metric_list:
            #     pprint(x.metric_key)
            #     pprint(x.percents)
            # input("waiting")
            for metric_key, trial_data in agg_percents.items():
                assert metric_key.PolicyCls
                row = {
                    "scenario_cls": data_key.scenario_config.ScenarioCls.__name__,
                    "AdoptingPolicyCls": (
                        data_key.scenario_config.AdoptPolicyCls.__name__
                    ),
                    "BasePolicyCls": data_key.scenario_config.BasePolicyCls.__name__,
                    "PolicyCls": metric_key.PolicyCls.__name__,
                    "outcome_type": metric_key.plane.name,
                    "as_group": metric_key.as_group.value,
                    "outcome": metric_key.outcome.name,
                    "percent_adopt": data_key.percent_adopt,
                    "propagation_round": data_key.propagation_round,
                    # trial_data can sometimes be empty
                    # for example, if we have 1 adopting AS for stubs_and_multihomed
                    # and that AS is multihomed, and not a stub, then for stubs,
                    # no ASes adopt, and trial_data is empty
                    # This is the proper way to do it, rather than defaulting trial_data
                    # to [0], which skews results when aggregating trials
                    "value": mean(trial_data) if trial_data else None,
                    "yerr": self._get_yerr(trial_data),
                    "scenario_config_label": data_key.scenario_config.csv_label,
                }
                rows.append(row)
        return rows

    def get_pickle_data(self):
        agg_data = list()
        for data_key, metric_list in self.data.items():
            agg_percents = sum(metric_list, start=metric_list[0]).percents
            for metric_key, trial_data in agg_percents.items():
                row = {
                    "data_key": data_key,
                    "metric_key": metric_key,
                    "value": mean(trial_data) if trial_data else None,
                    "yerr": self._get_yerr(trial_data),
                }
                agg_data.append(row)
        return agg_data

    def _get_yerr(self, trial_data: list[float]) -> float:
        """Returns 90% confidence interval for graphing"""

        if len(trial_data) > 1:
            yerr_num = 1.645 * 2 * stdev(trial_data)
            yerr_denom = sqrt(len(trial_data))
            return float(yerr_num / yerr_denom)
        else:
            return 0

    ######################
    # Track Metric Funcs #
    ######################

    def track_trial_metrics(
        self,
        *,
        engine: BaseSimulationEngine,
        percent_adopt: Union[float, SpecialPercentAdoptions],
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        outcomes: dict[int, dict[int, int]],
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
        engine: BaseSimulationEngine,
        percent_adopt: Union[float, SpecialPercentAdoptions],
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        outcomes: dict[int, dict[int, int]],
    ) -> None:
        """Tracks all metrics from a single trial, adding to self.data

        TODO: This should really be cleaned up, but good enough for now
        """

        metrics = [Metric(x, scenario.policy_classes_used) for x in self.metric_keys]
        self._populate_metrics(
            metrics=metrics, engine=engine, scenario=scenario, outcomes=outcomes
        )
        for metric in metrics:
            key = DataKey(
                propagation_round=propagation_round,
                percent_adopt=percent_adopt,
                scenario_config=scenario.scenario_config,
                metric_key=metric.metric_key,
            )
            self.data[key].append(metric)

    def _populate_metrics(
        self,
        *,
        metrics: list[Metric],
        engine: BaseSimulationEngine,
        scenario: Scenario,
        outcomes: dict[int, dict[int, int]],
    ) -> None:
        """Populates all metrics with data"""

        ctrl_plane_outcomes = outcomes[Plane.CTRL.value]
        data_plane_outcomes = outcomes[Plane.DATA.value]

        # Don't count these!
        uncountable_asns = scenario._untracked_asns

        for as_obj in engine.as_graph:
            # Don't count preset ASNs
            if as_obj.asn in uncountable_asns:
                continue
            for metric in metrics:
                # Must use .get, since if this tracking is turned off,
                # this will be an empty dict
                ctrl_plane_outcome = ctrl_plane_outcomes.get(
                    as_obj.asn, Outcomes.UNDETERMINED.value
                )
                data_plane_outcome = data_plane_outcomes.get(
                    as_obj.asn, Outcomes.UNDETERMINED.value
                )

                metric.add_data(
                    as_obj=as_obj,
                    engine=engine,
                    scenario=scenario,
                    ctrl_plane_outcome=ctrl_plane_outcome,
                    data_plane_outcome=data_plane_outcome,
                )
        # Only call this once or else it adds significant amounts of time
        for metric in metrics:
            metric.save_percents()

    def _track_trial_metrics_hook(
        self,
        *,
        engine: BaseSimulationEngine,
        percent_adopt: Union[float, SpecialPercentAdoptions],
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        outcomes,
    ) -> None:
        """Hook function for easy subclassing by a user"""

        pass
