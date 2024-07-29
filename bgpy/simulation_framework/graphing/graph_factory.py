from collections import defaultdict
from dataclasses import asdict, replace
from functools import cached_property
import gc
from itertools import product
from pathlib import Path
import pickle
from statistics import mean
from typing import Any

from frozendict import frozendict
import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
from tqdm import tqdm

from .line_info import LineInfo
from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_engine import Policy
from bgpy.simulation_framework.metric_tracker.metric_key import MetricKey
from bgpy.simulation_framework.utils import get_all_metric_keys




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
        strongest_attacker_legend_label: str = "Strongest Attacker"
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

        # Each metric key here contains plane, as group, and outcome
        # In other words, aech type of graph
        # This line combines that with adoption status
        graph_infos = list(product(self.metric_keys, [True, False, Any]))

        for metric_key, adopting in tqdm(
            graph_infos, total=len(graph_infos), desc="Writing Graphs"
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
        # metric_key: MetricKey
        #     Plane
        #     as_group
        #     outcome
        #     PolicyCls
        # Value: float
        # Yerr: yerr
        """

        relevant_rows = list()
        for row in self.graph_rows:
            # Get all the rows that correspond to that type of graph
            BasePolicyCls = row["data_key"].scenario_config.BasePolicyCls
            AdoptPolicyCls = row["data_key"].scenario_config.AdoptPolicyCls
            if (
                row["metric_key"].plane == metric_key.plane
                and row["metric_key"].as_group == metric_key.as_group
                and row["metric_key"].outcome == metric_key.outcome
                and (
                    (row["metric_key"].PolicyCls == BasePolicyCls and adopting is False)
                    or (
                        row["metric_key"].PolicyCls == AdoptPolicyCls
                        and adopting is True
                    )
                    or (row["metric_key"].PolicyCls == Policy and adopting is Any)
                )
            ):
                relevant_rows.append(row)
        return relevant_rows

    def _generate_graph(self, metric_key: MetricKey, relevant_rows, adopting) -> None:
        """Writes a graph to the graph dir"""

        if not relevant_rows:
            return

        graph_name = self._get_graph_name(metric_key, relevant_rows, adopting)

        label_rows_dict = defaultdict(list)
        for row in relevant_rows:
            label_rows_dict[row["data_key"].scenario_config.scenario_label].append(row)

        matplotlib.use("Agg")
        fig, ax = plt.subplots()

        self._customize_graph(fig, ax, metric_key)

        (
            non_aggregated_data_dict,
            max_attacker_data_dict,
        ) = self._graph_data(ax, label_rows_dict)

        self._add_legend(
            fig,
            ax,
            metric_key,
            relevant_rows,
            adopting,
            non_aggregated_data_dict,
            max_attacker_dict,
        )

        plt.tight_layout()

        self._save_and_close_graph(fig, ax, graph_name)

    def _get_graph_name(self, metric_key, relevant_rows, adopting) -> str:
        adopting_str = str(adopting) if isinstance(adopting, bool) else "Any"
        scenario_config = relevant_rows[0]["data_key"].scenario_config
        mod_name = scenario_config.preprocess_anns_func.__name__
        return (
            f"{scenario_config.ScenarioCls.__name__}_{mod_name}"
            f"/{metric_key.as_group.value}"
            f"/adopting_is_{adopting_str}"
            f"/{metric_key.plane.name}"
            f"/{metric_key.outcome.name}.png"
        ).replace(" ", "")

    def _customize_graph(self, fig, ax, metric_key):
        """Customizes graph properties"""

        fig.set_dpi(300)
        plt.rcParams.update({"font.size": 14, "lines.markersize": 10})
        # Set X and Y axis size
        plt.xlim(0, self.x_limit)
        plt.ylim(0, self.y_limit)
        # Set labels
        default_y_label = f"PERCENT {metric_key.outcome.name}".replace("_", " ")
        y_label = self.y_axis_label_replacement_dict.get(
            default_y_label, default_y_label
        )
        ax.set_ylabel(y_label)

        default_x_label = "Percent Adoption"
        x_label = self.x_axis_label_replacement_dict.get(
            default_x_label, default_x_label
        )
        ax.set_xlabel(x_label)

    def _graph_data(self, ax, label_rows_dict):

        # Used for random markers/line styles
        line_properties_generator = LinePropertiesGenerator()

        # Get the line data dict
        line_data_dict = dict()
        for label, graph_rows in label_rows_dict.items():
            line_data_dict[label] = self._get_line_data(label, graph_rows, line_properties_generator)

        # Add all lines that aren't aggregated into a strongest attacker aggregation
        self._plot_non_aggregated_lines(ax, line_data_dict)

        (
            non_aggregated_line_data_dict,
            max_attacker_data_dict
        ) = self._plot_strongest_attacker_line(ax, line_data_dict)
        return non_aggregated_line_data_dict, max_attacker_data_dict

    def _plot_strongest_attacker_line(ax, line_data_dict):

        max_attacker_data_dict = dict()
        # Add all lines that are aggregated
        for label in self.strongest_attacker_labels:
            max_attacker_data_dict[label] = line_data_dict.pop(label)

        scatter_plots = {label: {"xs": [], "ys": []} for label in self.strongest_attacker_labels}

        agg_xs = next(max_attacker_data_dict.values()).xs
        agg_ys = list()
        agg_yerrs = list()
        for i, x in enumerate(agg_xs):
            best_label = None
            max_val = None
            new_yerr = None
            for line_data in max_attacker_data_dict.values():
                if max_val is None or line_data.ys[i] > max_val:
                    best_label = line_data.label
                    max_val = line_data.ys[i]
                    new_yerr = line_data.yerrs[i]
            agg_ys.append(max_val)
            agg_yerrs.append(new_yerr)
            scatter_plots[label]["xs"].append(x)
            scatter_plots[label]["ys"].append(max_val)

        # NOTE: must use none to avoid plotting a marker here
        agg_line_data = LineData(
            self.strongest_attack_label,
            formatted_graph_rows=None,
            line_info=LineInfo(
                self.strongest_attack_label,
                marker=".",
                ls="solid",
                color="gray",
                _fmt="none"  # Suppresses markers
            ),
            xs=agg_xs,
            ys=agg_ys,
            yerrs=agg_yerrs,
        )






        raise NotImplementedError("Strongest attack plotting and adding to line data dict")

    def _get_line_data(self, label, graph_rows, line_properties_generator) -> LineData:
        """Gets the complete line data for a specific line"""

        formatted_graph_rows = self._get_formatted_graph_rows(graph_rows)

        line_info = self._get_line_info(label, line_properties_generator)

        xs = self._get_xs(formatted_graph_rows, line_info)
        ys = self._get_ys(formatted_graph_rows, line_info)
        yerrs = self._get_yerrs(formatted_graph_rows, line_info)

        return LineData(label=label, formatted_graph_rows=formatted_graph_rows, line_info=line_info, xs=xs, ys=ys, yerrs=yerrs)

    def _get_formatted_graph_rows(self, graph_rows):
        graph_rows_sorted = list(sorted(graph_rows, key=self._get_percent_adopt))
        # If no trial_data is present for a selection, value can be None
        # For example, if no stubs are selected to adopt, the graph for adopting
        # stub ASes will have no data points
        # This is proper, rather than defaulting to 0 or 100, which causes problems
        return [x for x in graph_rows_sorted if x["value"] is not None]

    def _get_percent_adopt(self, graph_row) -> float:
        """Extractions percent adoption for sort comparison

        Need separate function for mypy puposes
        Used in _generate_graph
        """

        percent_adopt = graph_row["data_key"].percent_adopt
        assert isinstance(percent_adopt, (float, SpecialPercentAdoptions))
        return float(percent_adopt)

    def _get_xs(self, graph_rows_sorted, line_info):
        """Gets the xs for a given line"""

        if line_info.override_xs:
            return line_info.override_xs
        else:
            return [float(x["data_key"].percent_adopt) * 100 for x in graph_rows_sorted]

    def _get_ys(self, graph_rows_sorted, line_info):
        """Gets the ys for a given line"""

        default_ys = [x["value"] for x in graph_rows_sorted]
        if line_info.override_ys:
            return line_info.override_ys
        # Line is unrelated to percent adoption, average together
        elif line_info.unrelated_to_adoption:
            return [mean(default_ys)] * len(default_ys)
        else:
            return default_ys

    def _get_yerrs(self, graph_rows_sorted, line_info):
        """Gets the yerrs for a given line"""

        default_yerrs = [x["yerr"] for x in graph_rows_sorted]
        if line_info.override_yerrs:
            return line_info.override_yerrs
        # Line is unrelated to percent adoption, average together
        elif line_info.unrelated_to_adoption:
            return [mean(default_yerrs)] * len(default_yerrs)
        else:
            return default_yerrs

    def _get_line_info(self, label, line_properties_generator) -> LineInfo:
        """Gets line info for a given label

        This pertains only to label, marker, and line styles, not x and y data
        i.e. info that is persistent accross the line
        """

        marker = line_properties_generator.get_marker()
        ls = line_properties_generator.get_line_style()
        color = line_properties_generator.get_color()
        line_info = LineInfo(label=label, marker=marker, ls=ls, color=color)

        if len(self.label_replacement_dict) > 0:
            # TODO: Deprecate
            return replace(
                line_info, label=self.label_replacement_dict.get(label, label)
            )
        else:
            return self.line_info_dict.get(label, line_info)

    def _plot_non_aggregated_lines(self, line_data_dict):
        """Add all lines that aren't aggregated into a strongest attacker aggregation"""

        for label, line_data in line_data_dict.items():
            if label not in self.strongest_attacker_labels:
                ax.errorbar(
                    line_data.xs,
                    line_data.ys,
                    line_data.yerrs,
                    label=line_data.line_info.label,
                    marker=line_data.line_info.marker,
                    ls=line_data.line_info.ls,
                    fmt=line_data.line_info._fmt,
                    color=line_data.color,
                )

    def _add_legend(self, fig, ax, metric_key, relevant_rows, adopting, non_aggregated_data_dict, max_attacker_data_dict):
        """Add legend to the graph"""

        # This is to avoid warnings
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels)

    def _save_and_close_graph(self, fig, ax, graph_name):
        """Saves and closes the graph"""

        path = self.graph_dir / graph_name
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(path)
        # https://stackoverflow.com/a/33343289/8903959
        ax.cla()
        plt.cla()
        plt.clf()
        # If you just close the fig, on machines with many CPUs and trials,
        # there is some sort of a memory leak that occurs. See stackoverflow
        # comment above
        plt.close(fig)
        # If you are running one simulation after the other, matplotlib
        # basically leaks memory. I couldn't find the original issue, but
        # here is a note in one of their releases saying to just call the garbage
        # collector: https://matplotlib.org/stable/users/prev_whats_new/
        # whats_new_3.6.0.html#garbage-collection-is-no-longer-run-on-figure-close
        # and here is the stackoverflow post on this topic:
        # https://stackoverflow.com/a/33343289/8903959
        # Even if this works without garbage collection in 3.5.2, that will break
        # as soon as we upgrade to the latest matplotlib which no longer does
        # If you run the simulations on a machine with many cores and lots of trials,
        # this bug leaks enough memory to crash the server, so we must garbage collect
        gc.collect()
