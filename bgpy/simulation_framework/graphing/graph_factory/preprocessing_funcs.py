from collections import defaultdict
from dataclasses import replace
from statistics import mean
from typing import TYPE_CHECKING

import matplotlib as mpl
import matplotlib.pyplot as plt

from bgpy.simulation_framework.graphing.line_data import LineData
from bgpy.simulation_framework.graphing.line_info import LineInfo
from bgpy.simulation_framework.graphing.line_properties_generator import (
    LinePropertiesGenerator,
)

if TYPE_CHECKING:
    from bgpy.simulation_framework.graph_data_aggregator import (
        DataPointAggData,
        DataPointKey,
        GraphCategory,
    )


def _preprocessing_steps(
    self,
    graph_category: "GraphCategory",
    data_dict: dict["DataPointKey", "DataPointAggData"],
):
    graph_name = self._get_graph_name(graph_category)

    label_rows_dict: defaultdict[str, list[DataPointAggData]] = defaultdict(list)
    for data_point_key, data in data_dict.items():
        label_rows_dict[data_point_key.scenario_config.scenario_label].append(data)

    mpl.use("Agg")
    fig, ax = plt.subplots()

    self._customize_graph(fig, ax, graph_category)

    line_data_dict = self._get_line_data_dict(ax, label_rows_dict)

    return graph_name, line_data_dict, fig, ax


def _get_graph_name(self, graph_category: "GraphCategory") -> str:
    return (
        f"{graph_category.as_group.value}"
        f"/in_adopting_asns_is_{graph_category.in_adopting_asns.value}"
        f"/{graph_category.plane.name}"
        f"/{graph_category.outcome.name}.png"
    ).replace(" ", "")


def _customize_graph(self, fig, ax, graph_category: "GraphCategory") -> None:
    """Customizes graph properties"""

    fig.set_dpi(300)
    plt.rcParams.update({"font.size": 14, "lines.markersize": 10})
    # Set X and Y axis size
    plt.xlim(0, self.x_limit)
    plt.ylim(0, self.y_limit)
    # Set labels
    default_y_label = f"PERCENT {graph_category.outcome.name}".replace("_", " ").title()
    y_label = self.y_axis_label_replacement_dict.get(default_y_label, default_y_label)
    ax.set_ylabel(y_label)

    default_x_label = "Percent Adoption".title()
    x_label = self.x_axis_label_replacement_dict.get(default_x_label, default_x_label)
    ax.set_xlabel(x_label)


def _get_line_data_dict(
    self, ax, label_rows_dict: defaultdict[str, list["DataPointAggData"]]
) -> dict[str, LineData]:
    # Used for random markers/line styles
    line_properties_generator = LinePropertiesGenerator()

    # Get the line data dict
    line_data_dict: dict[str, LineData] = dict()
    for label, graph_rows in label_rows_dict.items():
        line_data_dict[label] = self._get_line_data(
            label, graph_rows, line_properties_generator
        )

    self._add_hardcoded_lines_to_line_data_dict(line_data_dict)
    return line_data_dict


def _add_hardcoded_lines_to_line_data_dict(
    self, line_data_dict: dict[str, LineData]
) -> None:
    """Add hardcoded lines to the data dictionary"""

    for label, line_info in self.line_info_dict.items():
        # This is a hardcoded line that was not yet added
        if label not in line_data_dict and line_info.hardcoded_xs:
            line_data_dict[label] = LineData(
                label=label,
                formatted_graph_rows=None,
                line_info=line_info,
                xs=line_info.hardcoded_xs,
                ys=line_info.hardcoded_ys,
                yerrs=line_info.hardcoded_yerrs,
            )


def _get_line_data(
    self,
    label: str,
    graph_rows: list["DataPointAggData"],
    line_properties_generator: LinePropertiesGenerator,
) -> LineData:
    """Gets the complete line data for a specific line"""

    formatted_graph_rows: list[DataPointAggData] = sorted(
        graph_rows, key=self._get_percent_adopt
    )

    line_info = self._get_line_info(label, line_properties_generator)

    xs = self._get_xs(formatted_graph_rows, line_info)
    ys = self._get_ys(formatted_graph_rows, line_info)
    yerrs = self._get_yerrs(formatted_graph_rows, line_info)

    return LineData(
        label=line_info.label,
        formatted_graph_rows=formatted_graph_rows,
        line_info=line_info,
        xs=xs,
        ys=ys,
        yerrs=yerrs,
    )


def _get_percent_adopt(self, graph_row: "DataPointAggData") -> float:
    """Extractions percent adoption for sort comparison

    Need separate function for mypy puposes
    Used in _generate_graph
    """

    return float(graph_row.data_point_key.percent_adopt)


def _get_xs(
    self, graph_rows_sorted: list["DataPointAggData"], line_info: LineInfo
) -> tuple[float, ...]:
    """Gets the xs for a given line"""

    if line_info.hardcoded_xs:
        return line_info.hardcoded_xs
    else:
        return tuple(
            [float(x.data_point_key.percent_adopt) * 100 for x in graph_rows_sorted]
        )


def _get_ys(
    self, graph_rows_sorted: list["DataPointAggData"], line_info: LineInfo
) -> tuple[float, ...]:
    """Gets the ys for a given line"""

    default_ys = tuple([x.value for x in graph_rows_sorted])
    if line_info.hardcoded_ys:
        return line_info.hardcoded_ys
    # Line is unrelated to percent adoption, average together
    elif line_info.unrelated_to_adoption:
        return tuple([mean(default_ys)] * len(default_ys))
    else:
        return default_ys


def _get_yerrs(
    self, graph_rows_sorted: list["DataPointAggData"], line_info: LineInfo
) -> tuple[float, ...]:
    """Gets the yerrs for a given line"""

    default_yerrs = tuple([x.yerr for x in graph_rows_sorted])
    if line_info.hardcoded_yerrs:
        return line_info.hardcoded_yerrs
    # Line is unrelated to percent adoption, average together
    elif line_info.unrelated_to_adoption:
        return tuple([mean(default_yerrs)] * len(default_yerrs))
    else:
        return default_yerrs


def _get_line_info(
    self, label: str, line_properties_generator: LinePropertiesGenerator
) -> LineInfo:
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
        return replace(line_info, label=self.label_replacement_dict.get(label, label))
    else:
        rv = self.line_info_dict.get(label, line_info)
        assert isinstance(rv, LineInfo), "For Mypy"
        return rv
