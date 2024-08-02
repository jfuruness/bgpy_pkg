from collections import defaultdict
import csv
from math import sqrt
from pathlib import Path
import pickle
from statistics import mean
from statistics import stdev
from typing import Any, Optional, Union

from .data_point_key import DataPointKey
from .trial_data import TrialData
from .graph_category import GraphCategory

from bgpy.enums import Plane, SpecialPercentAdoptions, Outcomes
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_framework.scenarios import Scenario
from bgpy.simulation_framework.utils import get_all_graph_categories


class GraphDataAggregator:
    """Aggregates data for all the graphs"""

    def __init__(
        self,
        data: Optional[defaultdict[DataPointKey, list[float]]] = None,
        graph_categories: tuple[GraphCategory, ...] = tuple(
            list(get_all_graph_categories())
        ),
    ):
        """Inits data"""

        # Data is the key for single data point on a graph
        # key DataKey (prop_round, percent_adopt, scenario_label, MetricKey)
        # metric_key contains filtering info for the type of graph/data we collect
        if data:
            self.data: dict[GraphCategory, defaultdict[DataPointKey, list[float]]] = (
                data
            )
        else:
            self.data = {x: defaultdict(list) for x in graph_categories}

        self.graph_categories: tuple[GraphCategory, ...] = graph_categories

    #############
    # Add Funcs #
    #############

    def __add__(self, other):
        """Merges other GraphDataAggregator into this one and combines the data

        This gets called when we need to merge all the GraphDataAggregators
        from the various processes that were spawned
        """

        if isinstance(other, GraphDataAggregator):
            err = "All processes should use the same graph categories?"
            assert other.graph_categories == self.graph_categories, err
            # Deepcopy is slow, but fine here since it's only called once after sims
            # For BGPy __main__ using 100 trials, 3 percent adoptions, 1 scenario
            # on a lenovo laptop
            # 1.5s
            # new_data: defaultdict[DataKey, list[float]] = deepcopy(self.data)
            # .04s, but dangerous
            # new_data: defaultdict[DataKey, list[float]] = self.data
            # for k, v in other.data.items():
            #     new_data[k].extend(v)
            # .04s, not dangerous
            new_data: dict[GraphCategory, defaultdict[DataPointKey, list[float]]] = {
                x: defaultdict(list) for x in self.graph_categories
            }
            for obj in (self, other):
                for k, v in obj.data.items():
                    new_data[k].extend(v)
            return self.__class__(data=new_data)
        else:
            return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    ######################
    # Track Metric Funcs #
    ######################

    def aggregate_and_store_trial_data(
        self,
        *,
        engine: BaseSimulationEngine,
        percent_adopt: Union[float, SpecialPercentAdoptions],
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        outcomes: dict[int, dict[int, int]],
    ) -> None:
        """see desc

        Remember, each graph category represents a graph
        (Ex: Data plane, all ASes, attacker success, not adopting)
        Each DataPointKey represents a single point on that graph
        (Ex: 50% adoption of ROV against a prefix hijack)
        Each TrialData represents a single trial for a graph category
        and data point key comobo (gathered from all ases for that trial)

        The reason we don't simply save the engine to track metrics later
        is because the engines are very large and this would take a lot longer
        """

        # Each tracks trial data for a single graph category
        trial_datas = [TrialData(x) for x in self.graph_categories]
        self._aggregate_trial_data(
            trial_datas=trial_datas, engine=engine, scenario=scenario, outcomes=outcomes
        )

        data_point_key = DataPointKey(
            propagation_round=propagation_round,
            percent_adopt=percent_adopt,
            scenario_config=scenario.scenario_config,
        )

        for trial_data in trial_datas:
            # Cpmvert trial data as a percent
            # Ex: # of ASes attacker success and adopting / adopting
            self.data[trial_data.graph_category][data_point_key].append(
                trial_data.get_percent()
            )

    def _aggregate_trial_data(
        self,
        *,
        trial_datas: list[TrialData],
        engine: BaseSimulationEngine,
        scenario: Scenario,
        outcomes: dict[int, dict[int, int]],
    ) -> None:
        """Gets data from every AS and stores it in the trial datas"""

        ctrl_plane_outcomes = outcomes[Plane.CTRL.value]
        data_plane_outcomes = outcomes[Plane.DATA.value]

        # Don't count these!
        uncountable_asns = scenario._untracked_asns

        for as_obj in engine.as_graph:
            # Don't count preset ASNs
            if as_obj.asn in uncountable_asns:
                continue
            for trial_data in trial_datas:
                # Must use .get, since if this tracking is turned off,
                # this will be an empty dict
                ctrl_plane_outcome = ctrl_plane_outcomes.get(
                    as_obj.asn, Outcomes.UNDETERMINED.value
                )
                data_plane_outcome = data_plane_outcomes.get(
                    as_obj.asn, Outcomes.UNDETERMINED.value
                )

                trial_data.add_data(
                    as_obj=as_obj,
                    engine=engine,
                    scenario=scenario,
                    ctrl_plane_outcome=ctrl_plane_outcome,
                    data_plane_outcome=data_plane_outcome,
                )

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
        for graph_category, data_dict in self.data.items():
            for data_point_key, percent_list in data_dict.items():
                row = {
                    "scenario_cls": data_point_key.scenario_config.ScenarioCls.__name__,
                    "AdoptingPolicyCls": (
                        data_point_key.scenario_config.AdoptPolicyCls.__name__
                    ),
                    "BasePolicyCls": (
                        data_point_key.scenario_config.BasePolicyCls.__name__
                    ),
                    "in_adopting_asns": str(graph_category.in_adopting_asns),
                    "outcome_type": graph_category.plane.name,
                    "as_group": graph_category.as_group.value,
                    "outcome": graph_category.outcome.name,
                    "percent_adopt": data_point_key.percent_adopt,
                    "propagation_round": data_point_key.propagation_round,
                    # percent_list can sometimes be empty
                    # for example, if we have 1 adopting AS for stubs_and_multihomed
                    # and that AS is multihomed, and not a stub, then for stubs,
                    # no ASes adopt, and trial_data is empty
                    # This is the proper way to do it, rather than defaulting trial_data
                    # to [0], which skews results when aggregating trials
                    "value": mean(percent_list) if percent_list else None,
                    "yerr": self._get_yerr(percent_list),
                    "scenario_config_label": data_point_key.scenario_config.csv_label,
                    "scenario_label": data_point_key.scenario_config.scenario_label,
                }
                rows.append(row)
        return rows

    def get_pickle_data(self):
        agg_data = {x: dict() for x in self.graph_categories}
        for graph_category, data_dict in self.data.items():
            for data_point_key, percent_list in data_dict.items():
                agg_data[graph_category][data_point_key] = {
                    "value": mean(percent_list) if percent_list else None,
                    "yerr": self._get_yerr(percent_list),
                }
        return agg_data

    def _get_yerr(self, percent_list: list[float]) -> float:
        """Returns 90% confidence interval for graphing"""

        if len(percent_list) > 1:
            yerr_num = 1.645 * 2 * stdev(percent_list)
            yerr_denom = sqrt(len(percent_list))
            return float(yerr_num / yerr_denom)
        else:
            return 0
