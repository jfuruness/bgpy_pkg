from collections import defaultdict
from copy import deepcopy
from dataclass import fields
from typing import Any, Optional, Union

from .data_key import DataKey
from .metric import Metric
from .metric_factory import MetricFactory

from bgp_simulator_pkg.caida_collector.graph.base_as import AS
from bgp_simulator_pkg.enums import Plane, SpecialPercentAdoptions
from bgp_simulator_pkg.simulation_engine import SimulationEngine
from bgp_simulator_pkg.simulation_framework.scenarios import Scenario


class MetricTracker:
    """Tracks metrics used in graphs across trials"""

    def __init__(self, data: Optional[defaultdict[DataKey, list[Metric]]] = None):
        """Inits data"""

        # This is a list of all the trial info
        # You must save info trial by trial, so that you can join
        # After a return from multiprocessing
        # key DataKey (prop_round, percent_adopt, scenario_label, MetricCls)
        # value is a list of metric instances
        if data:
            self.data: defaultdict[DataKey, list[Metric]] = data
        else:
            self.data = defaultdict(list)

        self.metric_factory = MetricFactory()

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
            new_data: defaultdict[DataKey, list[Metric]] = deepcopy(self.data)
            for k, v in other.data.items():
                new_data[k].extend(v)
            return MetricTracker(data=new_data)
        else:
            return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

#############
# CSV Funcs #
#############

    @property
    def csv_headers(self) -> Tuple[str, ...]:
        """Returns headers used in CSV"""

        data_key_fields = [field.name for field in fields(DataKey)]
        other_fields = ["inner_label", "value"]
        return tuple(data_key_fields + other_fields)

    def get_csv_rows(self) -> list[dict[str, Any]]:
        """Returns rows for a CSV"""

        rows = list()
        for data_key, metric_list in self.data.items():
            agg_percents = sum(metric_list).percents
            for inner_label, final_val in agg_percents.items():
                values = list(asdict(data_key).values()) = [inner_label, final_val]
                rows.append({k: v for k, v in zip(self.csv_headers, values)})
        return rows

######################
# Track Metric Funcs #
######################

    def track_trial_metrics(
        self,
        *,
        engine: SimulationEngine,
        percent_adopt: Union[float, SpecialPercentAdoptions],
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
        percent_adopt: Union[float, SpecialPercentAdoptions],
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        outcomes,
    ) -> None:
        """Tracks all metrics from a single trial, adding to self.data

        TODO: This should really be cleaned up, but good enough for now
        """

        metrics = self.metric_factory.get_metric_subclasses()
        self._populate_metrics(
            metrics=metrics,
            engine=engine,
            scenario=scenario,
            outcomes=outcomes
        )
        for metric in metrics:
            key = DataKey(
                propagation_round=propagation_round,
                percent_adopt=percent_adopt,
                scenario_label=scenario.scenario_config.unique_data_label,
                MetricCls=metric.__class__,
            )
            self.data[key].append(metric)

    def _populate_metrics(
        self,
        *,
        metrics: list[Metric],
        engine: SimulationEngine,
        scenario: Scenario,
        outcomes,
    ) -> None:
        """Populates all metrics with data"""

        ctrl_plane_outcomes = outcomes[Plane.CTRL.value]
        data_plane_outcomes = outcomes[Plane.DATA.value]

        # Don't count these!
        uncountable_asns = scenario._preset_asns

        for as_obj in engine:
            # Don't count preset ASNs
            if as_obj.asn in uncountable_asns:
                continue
            for metric in metrics:
                metric.add_data(
                    as_obj=as_obj,
                    engine=engine,
                    scenario=scenario,
                    ctrl_plane_outcome=ctrl_plane_outcomes[as_obj],
                    data_plane_outcome=data_plane_outcomes[as_obj]
                )

    def _track_trial_metrics_hook(
        self,
        *,
        engine: SimulationEngine,
        percent_adopt: Union[float, SpecialPercentAdoptions],
        trial: int,
        scenario: Scenario,
        propagation_round: int,
        outcomes,
    ) -> None:
        """Hook function for easy subclassing by a user"""

        pass
