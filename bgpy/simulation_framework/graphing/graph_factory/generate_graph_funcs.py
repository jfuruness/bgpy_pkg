from bgpy.simulation_framework.metric_tracker.metric_key import MetricKey

from ..line_data import LineData
from ..line_info import LineInfo


def _generate_graph(self, metric_key: MetricKey, relevant_rows, adopting) -> None:
    """Writes a graph to the graph dir"""

    if not relevant_rows:
        return

    graph_name, line_data_dict, fig, ax = self._preprocessing_steps(
        metric_key, relevant_rows, adopting
    )

    (
        non_aggregated_data_dict,
        max_attacker_data_dict,
    ) = self._graph_data(ax, line_data_dict)

    self._add_legends_and_save(
        fig,
        ax,
        metric_key,
        relevant_rows,
        adopting,
        non_aggregated_data_dict,
        max_attacker_data_dict,
        graph_name,
    )


def _graph_data(self, ax, line_data_dict):
    # Add all lines that aren't aggregated into a strongest attacker aggregation
    self._plot_non_aggregated_lines(ax, line_data_dict)

    (
        non_aggregated_line_data_dict,
        max_attacker_data_dict,
    ) = self._plot_strongest_attacker_line(ax, line_data_dict)
    return non_aggregated_line_data_dict, max_attacker_data_dict


def _plot_non_aggregated_lines(self, ax, line_data_dict):
    """Add all lines that aren't aggregated into a strongest attacker aggregation"""

    for label, line_data in line_data_dict.items():
        if label not in self.strongest_attacker_labels:
            self._plot_line_data(ax, line_data)


def _plot_strongest_attacker_line(self, ax, line_data_dict):
    max_attacker_data_dict = dict()
    # Add all lines that are aggregated
    for label in self.strongest_attacker_labels:
        max_attacker_data_dict[label] = line_data_dict.pop(label)

    if self.strongest_attacker_labels:

        agg_xs, agg_ys, agg_yerrs, scatter_plots = self._get_agg_data(
            max_attacker_data_dict
        )
        agg_line_data = self._get_agg_line_data(agg_xs, agg_ys, agg_yerrs)

        line_data_dict[self.strongest_attacker_label] = agg_line_data

        self._plot_line_data(ax, agg_line_data)

        self._plot_scatter_plots(ax, scatter_plots, max_attacker_data_dict)

    return line_data_dict, max_attacker_data_dict


def _get_agg_data(self, max_attacker_data_dict):
    scatter_plots: dict[str, dict[str, list[float]]] = {  # type: ignore
        label: {"xs": [], "ys": []} for label in self.strongest_attacker_labels
    }

    # Populate the new agg line and scatter plots
    agg_xs = next(max_attacker_data_dict.values()).xs
    agg_ys = list()
    agg_yerrs = list()
    for i, x in enumerate(agg_xs):
        best_label = None
        max_val = None
        new_yerr = None
        for line_data in max_attacker_data_dict.values():
            if max_val is None or line_data.ys[i] > max_val:  # type: ignore
                best_label = line_data.label
                max_val = line_data.ys[i]
                new_yerr = line_data.yerrs[i]
        agg_ys.append(max_val)
        agg_yerrs.append(new_yerr)
        assert isinstance(best_label, str), "For mypy"
        assert isinstance(max_val, float), "For mypy"
        scatter_plots[best_label]["xs"].append(x)
        scatter_plots[best_label]["ys"].append(max_val)
    return agg_xs, agg_ys, agg_yerrs, scatter_plots


def _get_agg_line_data(self, agg_xs, agg_ys, agg_yerrs):
    return LineData(
        self.strongest_attack_label,
        formatted_graph_rows=None,
        line_info=LineInfo(
            self.strongest_attack_label,
            marker=".",
            ls="solid",
            color="gray",
            _fmt="none",  # Suppresses markers
        ),
        xs=agg_xs,
        ys=agg_ys,
        yerrs=agg_yerrs,
    )


def _plot_line_data(self, ax, line_data: LineData) -> None:
    """Plots line data"""

    ax.errorbar(
        line_data.xs,
        line_data.ys,
        line_data.yerrs,
        label=line_data.line_info.label,
        marker=line_data.line_info.marker,
        ls=line_data.line_info.ls,
        fmt=line_data.line_info._fmt,
        color=line_data.line_info.color,
    )


def _plot_scatter_plots(self, axs, scatter_plots, max_attacker_data_dict) -> None:
    # Plot scatter plots
    for label, point_dict in scatter_plots.items():
        axs.scatter(
            point_dict["xs"],
            point_dict["ys"],
            marker=max_attacker_data_dict[label].line_info.marker,
            ls=max_attacker_data_dict[label].line_info.ls,
            # Not needed I guess
            # label=max_attacker_data_dict[label].line_info.label,
            color=max_attacker_data_dict[label].line_info.color,
        )
