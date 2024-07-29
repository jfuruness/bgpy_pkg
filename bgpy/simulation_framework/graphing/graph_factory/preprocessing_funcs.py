from collections import defaultdict
from dataclasses import replace
from statistics import mean

import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

from bgpy.enums import SpecialPercentAdoptions

from ..line_data import LineData
from ..line_info import LineInfo
from ..line_properties_generator import LinePropertiesGenerator


def _preprocessing_steps(self, metric_key, relevant_rows, adopting):

    graph_name = self._get_graph_name(metric_key, relevant_rows, adopting)

    label_rows_dict = defaultdict(list)
    for row in relevant_rows:
        label_rows_dict[row["data_key"].scenario_config.scenario_label].append(row)

    matplotlib.use("Agg")
    fig, ax = plt.subplots()

    self._customize_graph(fig, ax, metric_key)

    line_data_dict = self._get_line_data_dict(ax, label_rows_dict)

    return graph_name, line_data_dict, fig, ax


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


def _get_line_data_dict(self, ax, label_rows_dict):
    # Used for random markers/line styles
    line_properties_generator = LinePropertiesGenerator()

    # Get the line data dict
    line_data_dict = dict()
    for label, graph_rows in label_rows_dict.items():
        line_data_dict[label] = self._get_line_data(
            label, graph_rows, line_properties_generator
        )

    self._add_hardcoded_lines_to_line_data_dict(line_data_dict)
    return line_data_dict


def _add_hardcoded_lines_to_line_data_dict(self, line_data_dict) -> None:
    """Add hardcoded lines to the data dictionary"""

    for label, line_info in self.line_info_dict.items():
        # This is a hardcoded line that was not yet added
        if (label not in line_data_dict and line_info.hardcoded_xs):
            line_data_dict[label] = LineData(
                label=label,
                formatted_graph_rows=None,
                line_info=line_info,
                xs=line_info.hardcoded_xs,
                ys=line_info.hardcoded_ys,
                yerrs=line_info.hardcoded_yerrs
            )


def _get_line_data(self, label, graph_rows, line_properties_generator) -> LineData:
    """Gets the complete line data for a specific line"""

    formatted_graph_rows = self._get_formatted_graph_rows(graph_rows)

    line_info = self._get_line_info(label, line_properties_generator)

    xs = self._get_xs(formatted_graph_rows, line_info)
    ys = self._get_ys(formatted_graph_rows, line_info)
    yerrs = self._get_yerrs(formatted_graph_rows, line_info)

    return LineData(
        label=label,
        formatted_graph_rows=formatted_graph_rows,
        line_info=line_info,
        xs=xs,
        ys=ys,
        yerrs=yerrs,
    )


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

    if line_info.hardcoded_xs:
        return line_info.hardcoded_xs
    else:
        return [float(x["data_key"].percent_adopt) * 100 for x in graph_rows_sorted]


def _get_ys(self, graph_rows_sorted, line_info):
    """Gets the ys for a given line"""

    default_ys = [x["value"] for x in graph_rows_sorted]
    if line_info.hardcoded_ys:
        return line_info.hardcoded_ys
    # Line is unrelated to percent adoption, average together
    elif line_info.unrelated_to_adoption:
        return [mean(default_ys)] * len(default_ys)
    else:
        return default_ys


def _get_yerrs(self, graph_rows_sorted, line_info):
    """Gets the yerrs for a given line"""

    default_yerrs = [x["yerr"] for x in graph_rows_sorted]
    if line_info.hardcoded_yerrs:
        return line_info.hardcoded_yerrs
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
