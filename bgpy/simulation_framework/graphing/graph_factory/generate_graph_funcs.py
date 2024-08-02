from dataclasses import replace

from frozendict import frozendict

from bgpy.simulation_framework.metric_tracker.metric_key import MetricKey

from ..line_data import LineData
from ..line_info import LineInfo


def _generate_graph(
    self, graph_category: GraphCategory, data_dict: dict[DataPointKey, dict[str, float]]
) -> None:
    """Writes a graph to the graph dir"""

    if not data_dict:
        return

    graph_name, line_data_dict, fig, ax = self._preprocessing_steps(
        graph_category, data_dict
    )

    (
        non_aggregated_data_dict,
        max_attacker_data_dict,
    ) = self._graph_data(ax, line_data_dict)

    self._add_legends_and_save(
        fig,
        ax,
        graph_category,
        non_aggregated_data_dict,
        max_attacker_data_dict,
        graph_name,
    )


def _graph_data(self, ax, line_data_dict: dict[str, LineData]):
    # Add all lines that aren't aggregated into a strongest attacker aggregation
    self._plot_non_aggregated_lines(ax, line_data_dict)

    (
        non_aggregated_line_data_dict,
        max_attacker_data_dict,
    ) = self._plot_strongest_attacker_line(ax, line_data_dict)
    return non_aggregated_line_data_dict, max_attacker_data_dict


def _plot_non_aggregated_lines(self, ax, line_data_dict: dict[str, LineData]) -> None:
    """Add all lines that aren't aggregated into a strongest attacker aggregation"""

    for label, line_data in line_data_dict.items():
        if label not in self.strongest_attacker_labels:
            self._plot_line_data(ax, line_data)


def _plot_strongest_attacker_line(self, ax, line_data_dict: dict[str, LineData]):
    max_attacker_data_dict = dict()
    # Add all lines that are aggregated
    for label in self.strongest_attacker_labels:
        max_attacker_data_dict[label] = line_data_dict.pop(label)

    if self.strongest_attacker_labels:

        agg_xs, agg_ys, agg_yerrs, scatter_line_data_dict = self._get_agg_data(
            max_attacker_data_dict
        )
        agg_line_data = self._get_agg_line_data(agg_xs, agg_ys, agg_yerrs)

        line_data_dict[self.strongest_attacker_legend_label] = agg_line_data

        self._plot_line_data(ax, agg_line_data)

        self._plot_scatter_plots(ax, scatter_line_data_dict)

    return line_data_dict, max_attacker_data_dict


def _get_agg_data(self, max_attacker_data_dict):
    scatter_plots: dict[str, dict[str, list[float]]] = {  # type: ignore
        label: {"xs": [], "ys": [], "yerrs": []}
        for label in self.strongest_attacker_labels
    }

    # Populate the new agg line and scatter plots
    agg_xs = list(max_attacker_data_dict.values())[0].xs
    agg_ys = list()
    agg_yerrs = [0 for _ in agg_xs]
    for i, x in enumerate(agg_xs):
        best_label = None
        max_val = None
        new_yerr = None
        for label, line_data in max_attacker_data_dict.items():
            if max_val is None or line_data.ys[i] > max_val:  # type: ignore
                best_label = label
                max_val = line_data.ys[i]
                new_yerr = line_data.yerrs[i]
        agg_ys.append(max_val)
        assert isinstance(best_label, str), "For mypy"
        assert isinstance(max_val, float), "For mypy"
        assert isinstance(new_yerr, float), "For mypy"
        scatter_plots[best_label]["xs"].append(x)
        scatter_plots[best_label]["ys"].append(max_val)
        scatter_plots[best_label]["yerrs"].append(new_yerr)

    scatter_line_data_dict = self._get_scatter_line_data_dict(
        scatter_plots, max_attacker_data_dict
    )
    return agg_xs, agg_ys, agg_yerrs, scatter_line_data_dict


def _get_scatter_line_data_dict(self, scatter_plots, max_attacker_dict):
    """Converts scatter plots into proper line data for plotting"""

    scatter_line_data_dict = dict()
    for label, point_dict in scatter_plots.items():
        old_line_data = max_attacker_dict[label]

        scatter_line_data_dict[label] = LineData(
            label=old_line_data.label,
            formatted_graph_rows=None,
            # This makes the line dissapear
            line_info=replace(
                old_line_data.line_info,
                ls="solid",
                color="grey",
                extra_kwargs={
                    **dict(old_line_data.line_info.extra_kwargs),
                    **{
                        # Marker face color
                        "mfc": old_line_data.line_info.color,
                        # Marker edge color
                        "mec": old_line_data.line_info.color,
                        # Marker size
                        "ms": 20,
                        "markeredgewidth": 3,
                        # Old line color
                        "ecolor": old_line_data.line_info.color,
                        "zorder": 3,
                    },
                },
            ),
            xs=point_dict["xs"],
            ys=point_dict["ys"],
            yerrs=point_dict["yerrs"],
        )
    return scatter_line_data_dict


def _get_agg_line_data(self, agg_xs, agg_ys, agg_yerrs):
    return LineData(
        self.strongest_attacker_legend_label,
        formatted_graph_rows=None,
        line_info=LineInfo(
            self.strongest_attacker_legend_label,
            marker=".",
            ls="solid",
            color="gray",
            # Ms stands for marker size
            extra_kwargs=frozendict({"zorder": 0, "ms": 0, "elinewidth": 0}),
        ),
        xs=agg_xs,
        ys=agg_ys,
        yerrs=agg_yerrs,
    )


def _plot_line_data(self, ax, line_data: LineData):
    """Plots line data"""

    return ax.errorbar(
        line_data.xs,
        line_data.ys,
        line_data.yerrs,
        label=line_data.line_info.label,
        marker=line_data.line_info.marker,
        ls=line_data.line_info.ls,
        color=line_data.line_info.color,
        **line_data.line_info.extra_kwargs,
    )


def _plot_scatter_plots(self, ax, scatter_plot_line_data_dict):
    """Plots scatter plots"""

    for line_data in scatter_plot_line_data_dict.values():
        self._plot_line_data(ax, line_data)
