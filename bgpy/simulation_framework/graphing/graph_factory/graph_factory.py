from itertools import product
from pathlib import Path
import pickle
from typing import Any

from frozendict import frozendict
from tqdm import tqdm

from bgpy.simulation_engine import Policy
from bgpy.simulation_framework.metric_tracker.metric_key import MetricKey
from bgpy.simulation_framework.utils import get_all_metric_keys

from ..line_info import LineInfo

# NOTE: mypy won't accept these unless they're outside the class
from .preprocessing_funcs import (
    _preprocessing_steps,
    _get_graph_name,
    _customize_graph,
    _get_line_data_dict,
    _add_hardcoded_lines_to_line_data_dict,
    _get_line_data,
    _get_formatted_graph_rows,
    _get_percent_adopt,
    _get_xs,
    _get_ys,
    _get_yerrs,
    _get_line_info,
)
from .generate_graph_funcs import (
    _generate_graph,
    _graph_data,
    _plot_non_aggregated_lines,
    _plot_strongest_attacker_line,
    _get_agg_data,
    _get_agg_line_data,
    _get_scatter_line_data_dict,
    _plot_line_data,
    _plot_scatter_plots,
)

from .add_legends_and_save_funcs import (
    _add_legends_and_save,
    _add_legend,
    _add_strongest_attacker_legend,
    _save_and_close_graph,
)


class GraphFactory:
    """Automates graphing of default graphs"""

    def __init__(
        self,
        pickle_path: Path,
        graph_dir: Path,
        # A nice way to substitute labels post run
        label_replacement_dict=frozendict(),
        y_axis_label_replacement_dict=frozendict(),
        x_axis_label_replacement_dict=frozendict(),
        x_limit: int = 100,
        y_limit: int = 100,
        metric_keys: tuple[MetricKey, ...] = tuple(list(get_all_metric_keys())),
        line_info_dict: frozendict[str, LineInfo] = frozendict(),
        strongest_attacker_labels: tuple[str, ...] = (),
        strongest_attacker_legend_label: str = "Strongest Attacker",
    ) -> None:
        self.pickle_path: Path = pickle_path
        with self.pickle_path.open("rb") as f:
            self.graph_rows = self._get_filtered_graph_rows(pickle.load(f))
        self.graph_dir: Path = graph_dir
        self.graph_dir.mkdir(parents=True, exist_ok=True)

        self.label_replacement_dict = label_replacement_dict
        self.x_axis_label_replacement_dict = x_axis_label_replacement_dict
        self.y_axis_label_replacement_dict = y_axis_label_replacement_dict
        self.x_limit = x_limit
        self.y_limit = y_limit
        self.metric_keys: tuple[MetricKey, ...] = metric_keys
        self.line_info_dict = line_info_dict
        self.strongest_attacker_labels: tuple[str, ...] = strongest_attacker_labels
        self.strongest_attacker_legend_label: str = strongest_attacker_legend_label

    def _get_filtered_graph_rows(self, rows_from_pickle):
        """Get only the latest propagation round, or raise an error"""

        # Find the latest propagation round
        max_prop_round = max(x["data_key"].propagation_round for x in rows_from_pickle)
        # Get only data from the latest propagation round
        graph_rows = [
            x
            for x in rows_from_pickle
            if x["data_key"].propagation_round == max_prop_round
        ]

        # Ensure that we aren't comparing differing numbers of propagation rounds
        propagation_rounds = [
            x["data_key"].scenario_config.propagation_rounds for x in graph_rows
        ]
        if len(set(propagation_rounds)) != 1:
            raise NotImplementedError(
                "Default grapher doesn't account for differing propagation rounds, "
                "You'll need to write your own GraphFactory and pass it into "
                "sim.run with sim.run(GraphFactoryCls=MyGraphFactoryCls)"
            )

        return graph_rows

    def generate_graphs(self) -> None:
        """Generates default graphs"""

        # Each metric key contains the type of graph
        for metric_key in tqdm(
            self.metric_keys, total=len(self.metric_keys), desc="Writing Graphs"
        ):
            relevant_rows = self._get_relevant_rows(metric_key, adopting)
            self._generate_graph(metric_key, relevant_rows, adopting=adopting)

    def _get_relevant_rows(self, metric_key, adopting: bool):
        """Gets the relevant graphing rows for a given metric_key/graph

        # Row is:
        # data_key: DataKey
        #    propagation_round
        #    percent_adopt
        #    scenario_config
        #     metric_key: MetricKey
        #         Plane
        #         as_group
        #         outcome
        #         in_adopting_asns
        # Value: float
        # Yerr: yerr

        DataKey is the point for a scenario_config, like 50% adoption
        of prefix hijack against ROV. MetricKey is the type of graph.
        So for each metric key - get all data points for that graph and
        graph them
        """

        relevant_rows = list()
        for row in self.graph_rows:
            # Get all the rows that correspond to that type of graph
            if row["data_key"].metric_key == metric_key:
                relevant_rows.append(row)
        return relevant_rows

    # NOTE: mypy won't accept these unless they're outside the class
    # Preprocess funcs
    _preprocessing_steps = _preprocessing_steps
    _get_graph_name = _get_graph_name
    _customize_graph = _customize_graph
    _get_line_data_dict = _get_line_data_dict
    _add_hardcoded_lines_to_line_data_dict = _add_hardcoded_lines_to_line_data_dict
    _get_line_data = _get_line_data
    _get_formatted_graph_rows = _get_formatted_graph_rows
    _get_percent_adopt = _get_percent_adopt
    _get_xs = _get_xs
    _get_ys = _get_ys
    _get_yerrs = _get_yerrs
    _get_line_info = _get_line_info
    # Generate=Generate graph=graph funcs=funcs
    _generate_graph = _generate_graph
    _graph_data = _graph_data
    _plot_non_aggregated_lines = _plot_non_aggregated_lines
    _plot_strongest_attacker_line = _plot_strongest_attacker_line
    _get_agg_data = _get_agg_data
    _get_agg_line_data = _get_agg_line_data
    _get_scatter_line_data_dict = _get_scatter_line_data_dict
    _plot_line_data = _plot_line_data
    _plot_scatter_plots = _plot_scatter_plots

    # Add=Add legends=legends and=and save=save funcs=funcs
    _add_legends_and_save = _add_legends_and_save
    _add_legend = _add_legend
    _add_strongest_attacker_legend = _add_strongest_attacker_legend
    _save_and_close_graph = _save_and_close_graph
