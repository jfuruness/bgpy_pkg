from dataclasses import replace
from typing import TYPE_CHECKING

from frozendict import frozendict

from bgpy.simulation_framework.graphing.line_data import LineData
from bgpy.simulation_framework.graphing.line_info import LineInfo

if TYPE_CHECKING:
    from bgpy.simulation_framework import DataPointAggData, DataPointKey, GraphCategory


def _generate_graph(
    self,
    graph_category: "GraphCategory",
    data_dict: dict["DataPointKey", "DataPointAggData"],
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
    ) = self._plot_strongest_attacker_lines(ax, line_data_dict)
    return non_aggregated_line_data_dict, max_attacker_data_dict


def _plot_non_aggregated_lines(self, ax, line_data_dict: dict[str, LineData]) -> None:
    """Add all lines that aren't aggregated into a strongest attacker aggregation"""

    for label, line_data in line_data_dict.items():
        # Labels to aggregate for the strongest attacker shouldn't be plotted
        if label not in self.labels_to_aggregate:
            self._plot_line_data(ax, line_data)


def _plot_strongest_attacker_lines(
    self, ax, line_data_dict: dict[str, LineData]
) -> tuple[dict[str, LineData], dict[str, LineData]]:
    # Add all lines that are aggregated
    max_attacker_data_dict: dict[str, LineData] = dict()
    for label in self.labels_to_aggregate:
        line_infos = line_data_dict.pop(label, None)
        assert line_infos, "Did you pass in the wrong strongest attacker dict?"
        max_attacker_data_dict[label] = line_infos
    # At this point max_attacker_data_dict might be something like:
    # {ASPA: (ASPAForgedOriginLineInfo, ASPAShortestPathLineInfo)

    if self.labels_to_aggregate:
        strongest_agg_dict, scatter_line_data_dict = self._get_agg_data(
            max_attacker_data_dict
        )

        agg_line_datas = self._get_agg_line_data(strongest_agg_dict)

        for agg_line_data in agg_line_datas:
            line_data_dict[agg_line_data.label] = agg_line_data
            self._plot_line_data(ax, agg_line_data)

        self._plot_scatter_plots(ax, scatter_line_data_dict)

    return line_data_dict, max_attacker_data_dict


def _get_agg_data(
    self, max_attacker_data_dict: dict[str, LineData]
) -> tuple[dict[str, dict[str, list[float]]], dict[str, LineData]]:
    # Gets all lines that will be in the scatter plot
    # So basically each line beforehand, but some X values will
    # be removed if they aren't the strongest listed
    scatter_plots: dict[str, dict[str, list[float]]] = {
        label: {"xs": [], "ys": [], "yerrs": []} for label in self.labels_to_aggregate
    }

    # Get all strongest attacker lines. No data point markers, but the
    # line itself that will be plotted
    agg_xs = next(iter(max_attacker_data_dict.values())).xs
    strongest_agg_dict: dict[str, dict[str, list[float]]] = {
        label: {"agg_xs": list(agg_xs), "agg_ys": [], "agg_yerrs": [0 for _ in agg_xs]}
        for label in self.strongest_attacker_dict
    }

    # Populate the new agg line and scatter plots
    for (
        strongest_attacker_label,
        line_infos_to_agg,
    ) in self.strongest_attacker_dict.items():
        # {agg_xs, agg_ys, agg_yerrs}
        cur_data = strongest_agg_dict[strongest_attacker_label]

        for i, x in enumerate(cur_data["agg_xs"]):
            best_label = None
            max_val = None
            new_yerr = None
            for line_info in line_infos_to_agg:
                line_data = max_attacker_data_dict[line_info.label]
                # mypy doens't understand that line_infos_to_agg > len 1
                if max_val is None or line_data.ys[i] > max_val:  # type: ignore
                    best_label = line_info.label
                    max_val = line_data.ys[i]
                    new_yerr = line_data.yerrs[i]
            assert isinstance(best_label, str), "For mypy"
            assert isinstance(max_val, float), "For mypy"
            assert isinstance(new_yerr, (float, int)), f"mypy {line_infos_to_agg}"
            cur_data["agg_ys"].append(max_val)
            scatter_plots[best_label]["xs"].append(x)
            scatter_plots[best_label]["ys"].append(max_val)
            scatter_plots[best_label]["yerrs"].append(new_yerr)

    scatter_line_data_dict = self._get_scatter_line_data_dict(
        scatter_plots, max_attacker_data_dict
    )
    return strongest_agg_dict, scatter_line_data_dict


def _get_scatter_line_data_dict(
    self,
    scatter_plots: dict[str, dict[str, list[float]]],
    max_attacker_dict: dict[str, LineData],
) -> dict[str, LineData]:
    """Converts scatter plots into proper line data for plotting"""

    label_to_marker_dict = dict()
    for line_info_tup in self.strongest_attacker_dict.values():
        for line_info in line_info_tup:
            label_to_marker_dict[line_info.strongest_attacker_legend_label] = (
                line_info.marker
            )

    scatter_line_data_dict = dict()
    for label, point_dict in scatter_plots.items():
        old_line_data = max_attacker_dict[label]

        scatter_line_data_dict[label] = LineData(
            label=old_line_data.label,
            formatted_graph_rows=None,
            # This makes the line dissapear
            line_info=replace(
                old_line_data.line_info,
                marker=label_to_marker_dict[
                    old_line_data.line_info.strongest_attacker_legend_label
                ],
                ls="solid",
                color="grey",
                extra_kwargs=frozendict(
                    {
                        **dict(
                            lw=0,
                            **old_line_data.line_info.extra_kwargs,
                        ),
                        # Marker face color
                        # Since lines are colored, make color grey (jk)
                        "mfc": old_line_data.line_info.color,
                        # Marker edge color
                        "mec": old_line_data.line_info.color,
                        # Marker size
                        # "ms": 20,
                        # "markeredgewidth": 3,
                        # Old line color
                        "ecolor": old_line_data.line_info.color,
                        "zorder": 3,
                    }
                ),
            ),
            xs=tuple(point_dict["xs"]),
            ys=tuple(point_dict["ys"]),
            yerrs=tuple(point_dict["yerrs"]),
        )
    return scatter_line_data_dict


def _get_agg_line_data(
    self, strongest_agg_dict: dict[str, dict[str, list[float]]]
) -> tuple[LineData, ...]:
    line_datas = list()
    for agg_label, agg_data_dict in strongest_agg_dict.items():
        line_datas.append(
            LineData(
                agg_label,
                formatted_graph_rows=None,
                line_info=LineInfo(
                    agg_label,
                    marker=".",
                    # Reuse the same line style and color as the aggregated lines
                    ls=self.strongest_attacker_dict[agg_label][0].ls,
                    color=self.strongest_attacker_dict[agg_label][0].color,
                    # Ms stands for marker size
                    extra_kwargs=frozendict({"zorder": 0, "ms": 0, "elinewidth": 0}),
                ),
                xs=tuple(agg_data_dict["agg_xs"]),
                ys=tuple(agg_data_dict["agg_ys"]),
                yerrs=tuple(agg_data_dict["agg_yerrs"]),
            )
        )
    return tuple(line_datas)


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


def _plot_scatter_plots(
    self, ax, scatter_plot_line_data_dict: dict[str, LineData]
) -> None:
    """Plots scatter plots"""

    for line_data in scatter_plot_line_data_dict.values():
        self._plot_line_data(ax, line_data)
