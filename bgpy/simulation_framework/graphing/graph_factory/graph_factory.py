import pickle
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from frozendict import frozendict
from tqdm import tqdm

from bgpy.simulation_framework.graphing.line_info import LineInfo

from .add_legends_and_save_funcs import (
    _add_legend,
    _add_legends_and_save,
    _add_strongest_attacker_legend,
    _save_and_close_graph,
)
from .generate_graph_funcs import (
    _generate_graph,
    _get_agg_data,
    _get_agg_line_data,
    _get_scatter_line_data_dict,
    _graph_data,
    _plot_line_data,
    _plot_non_aggregated_lines,
    _plot_scatter_plots,
    _plot_strongest_attacker_lines,
)

# NOTE: mypy won't accept these unless they're outside the class
from .preprocessing_funcs import (
    _add_hardcoded_lines_to_line_data_dict,
    _customize_graph,
    _get_graph_name,
    _get_line_data,
    _get_line_data_dict,
    _get_line_info,
    _get_percent_adopt,
    _get_xs,
    _get_yerrs,
    _get_ys,
    _preprocessing_steps,
)

if TYPE_CHECKING:
    from bgpy.simulation_framework.graph_data_aggregator.graph_data_aggregator import (
        PICKLE_DATA_TYPE,
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
        strongest_attacker_dict: frozendict[str, tuple[LineInfo, ...]] = frozendict(),
        labels_to_remove: frozenset[str] = frozenset(),
        add_legend: bool = True,
    ) -> None:
        self.add_legend = add_legend
        self.labels_to_remove: frozenset[str] = labels_to_remove
        self.pickle_path: Path = pickle_path
        with self.pickle_path.open("rb") as f:
            self.graph_data: PICKLE_DATA_TYPE = (
                self._get_last_propagation_round_graph_data(
                    pickle.load(f)  # noqa: S301
                )
            )

        self.graph_data = self._remove_labels()
        self.graph_dir: Path = graph_dir
        self.graph_dir.mkdir(parents=True, exist_ok=True)

        self.label_replacement_dict = label_replacement_dict
        self.x_axis_label_replacement_dict = x_axis_label_replacement_dict
        self.y_axis_label_replacement_dict = y_axis_label_replacement_dict
        self.x_limit = x_limit
        self.y_limit = y_limit
        # Get all the labels included to filter line_info_dict and strongest_attackerdct
        labels = set()
        for data_dict in self.graph_data.values():
            for data_point_key in data_dict:
                labels.add(data_point_key.scenario_config.scenario_label)

        # Filter these to only include relevant labels/infos
        self.line_info_dict = {
            k: v for k, v in line_info_dict.items() if k in labels or v.hardcoded_xs
        }
        self.strongest_attacker_dict: frozendict[str, tuple[LineInfo, ...]] = (
            frozendict(
                {
                    k: tuple([x for x in v if x.label in labels])
                    for k, v in strongest_attacker_dict.items()
                    if tuple([x for x in v if x.label in labels])
                }
            )
        )

    def _get_last_propagation_round_graph_data(
        self, pickle_graph_data: "PICKLE_DATA_TYPE"
    ) -> "PICKLE_DATA_TYPE":
        """Get only the latest propagation round for each scenario

        or raise an error
        """

        scenario_labels_max_round = dict()
        for data_dict in pickle_graph_data.values():
            for data_point_key in data_dict:
                scenario_labels_max_round[
                    data_point_key.scenario_config.scenario_label
                ] = 0

        # Find the latest propagation round
        for data_dict in pickle_graph_data.values():
            for data_point_key in data_dict:
                label = data_point_key.scenario_config.scenario_label
                scenario_labels_max_round[label] = max(
                    data_point_key.propagation_round, scenario_labels_max_round[label]
                )

        filtered_graph_data: PICKLE_DATA_TYPE = {x: dict() for x in pickle_graph_data}
        # Get only data from the latest propagation round for each scenario label
        for graph_category, data_dict in pickle_graph_data.items():
            for data_point_key, data in data_dict.items():
                label = data_point_key.scenario_config.scenario_label
                max_propagation_round = scenario_labels_max_round[label]
                if data_point_key.propagation_round == max_propagation_round:
                    filtered_graph_data[graph_category][data_point_key] = data
                    err = (
                        "These two numbers should be the same. "
                        f"{data_point_key.propagation_round + 1} "
                        f"{data_point_key.scenario_config.propagation_rounds} "
                    )
                    # Add one due to index 0 when comparing to total
                    assert data_point_key.propagation_round + 1 == (
                        data_point_key.scenario_config.propagation_rounds
                    ), err

        return filtered_graph_data

    def _remove_labels(self) -> "PICKLE_DATA_TYPE":
        """Removes labels from labels_to_remove"""

        new_data: PICKLE_DATA_TYPE = dict()
        for graph_category, data_dict in self.graph_data.items():
            for data_point_key, data in data_dict.items():
                label = data_point_key.scenario_config.scenario_label
                if label not in self.labels_to_remove:
                    if graph_category not in new_data:
                        new_data[graph_category] = dict()
                    new_data[graph_category][data_point_key] = data
        return new_data

    def generate_graphs(self) -> None:
        """Generates default graphs"""

        # Each metric key contains the type of graph
        for graph_category, data_dict in tqdm(
            self.graph_data.items(),
            total=len(self.graph_data),
            desc=f"Graphing {self.pickle_path.parent}",
        ):
            self._generate_graph(graph_category, data_dict)

    @cached_property
    def labels_to_aggregate(self) -> frozenset[str]:
        """Returns labels to aggregate for the strongest attacker labels"""

        labels_to_aggregate: set[str] = set()
        for line_infos in self.strongest_attacker_dict.values():
            for line_info in line_infos:
                labels_to_aggregate.add(line_info.label)
        return frozenset(labels_to_aggregate)

    # NOTE: mypy won't accept these unless they're outside the class
    # Preprocess funcs
    _preprocessing_steps = _preprocessing_steps
    _get_graph_name = _get_graph_name
    _customize_graph = _customize_graph
    _get_line_data_dict = _get_line_data_dict
    _add_hardcoded_lines_to_line_data_dict = _add_hardcoded_lines_to_line_data_dict
    _get_line_data = _get_line_data
    _get_percent_adopt = _get_percent_adopt
    _get_xs = _get_xs
    _get_ys = _get_ys
    _get_yerrs = _get_yerrs
    _get_line_info = _get_line_info
    # Generate=Generate graph=graph funcs=funcs
    _generate_graph = _generate_graph
    _graph_data = _graph_data
    _plot_non_aggregated_lines = _plot_non_aggregated_lines
    _plot_strongest_attacker_lines = _plot_strongest_attacker_lines
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
