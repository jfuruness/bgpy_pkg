from itertools import product
from pathlib import Path
import pickle
from typing import Any

from frozendict import frozendict
from tqdm import tqdm

from bgpy.simulation_engine import Policy
from bgpy.simulation_framework.metric_tracker.metric_key import MetricKey
from bgpy.simulation_framework.utils import get_all_graph_categories

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
        line_info_dict: frozendict[str, LineInfo] = frozendict(),
        strongest_attacker_labels: tuple[str, ...] = (),
        strongest_attacker_legend_label: str = "Strongest Attacker",
    ) -> None:
        self.pickle_path: Path = pickle_path
        with self.pickle_path.open("rb") as f:
            self.graph_data = self._get_last_propagation_round_graph_data(
                pickle.load(f)
            )
        self.graph_dir: Path = graph_dir
        self.graph_dir.mkdir(parents=True, exist_ok=True)

        self.label_replacement_dict = label_replacement_dict
        self.x_axis_label_replacement_dict = x_axis_label_replacement_dict
        self.y_axis_label_replacement_dict = y_axis_label_replacement_dict
        self.x_limit = x_limit
        self.y_limit = y_limit
        self.line_info_dict = line_info_dict
        self.strongest_attacker_labels: tuple[str, ...] = strongest_attacker_labels
        self.strongest_attacker_legend_label: str = strongest_attacker_legend_label

    def _get_last_propagation_round_graph_data(self, pickle_graph_data):
        """Get only the latest propagation round, or raise an error"""

        # Find the latest propagation round
        max_propagation_round = 0
        for data_dict in pickle_graph_data.values():
            for data_point_key in data_dict:
                max_propagation_round = max(
                    data_point_key.propagation_round, propagation_round
                )

        filtered_graph_data = {x: dict() for x in pickle_graph_data}
        # Get only data from the latest propagation round
        for graph_category, data_dict in pickle_graph_data.items():
            for data_point_key, data in data_dict.items():
                if data_point_key.propagation_round == max_propagation_round:
                    filtered_graph_data[data_point_key] = data
                    assert data_point_key.propagation_round == (
                        data_point_key.scenario_config.propagation_rounds
                    ), "These two numbers should be the same"

        return filtered_graph_data

    def generate_graphs(self) -> None:
        """Generates default graphs"""

        # Each metric key contains the type of graph
        for graph_category, data_dict in tqdm(
            self.graph_data.items(), total=len(self.graph_data), desc="Graphing"
        ):
            self._generate_graph(graph_category, data_dict)

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
