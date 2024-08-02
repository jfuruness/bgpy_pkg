from collections import defaultdict
from dataclasses import replace
from statistics import mean

import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

from bgpy.enums import SpecialPercentAdoptions

from ..line_data import LineData
from ..line_info import LineInfo
from ..line_properties_generator import LinePropertiesGenerator


def _preprocessing_steps(
    self, graph_category: GraphCategory, data_dict: dict[DataPointKey, dict[str, float]]
):

    graph_name = self._get_graph_name(graph_category)

    label_rows_dict: defaultdict[str, list[dict[str, float | DataPointKey]]] = (
        defaultdict(list)
    )
    for data_point_key, data in data_dict.items():
        new_data: dict[str, float | DataPointKey] = data.copy()
        new_data["data_point_key"] = data_point_key
        label_rows_dict[data_point_key.scenario_config.scenario_label].append(new_data)

    matplotlib.use("Agg")
    fig, ax = plt.subplots()

    self._customize_graph(fig, ax, graph_category)

    line_data_dict = self._get_line_data_dict(ax, label_rows_dict)

    return graph_name, line_data_dict, fig, ax


def _get_graph_name(self, graph_category: GraphCategory) -> str:

    return (
        f"{graph_category.as_group.value}"
        f"/in_adopting_asns_is_{graph_category.in_adopting_asns}"
        f"/{graph_category.plane.name}"
        f"/{graph_category.outcome.name}.png"
    ).replace(" ", "")


def _customize_graph(self, fig, ax, graph_category: GraphCategory):
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
    self, ax, label_rows_dict: defaultdict[str, list[dict[str, float | DataPointKey]]]
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
    graph_rows: list[dict[str, float | DataPointKey]],
    line_properties_generator: LinePropertiesGenerator,
) -> LineData:
    """Gets the complete line data for a specific line"""

    formatted_graph_rows = self._get_formatted_graph_rows(graph_rows)

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


def _get_formatted_graph_rows(
    self, graph_rows: list[dict[str, float | DataPointKey]]
) -> list[dict[str, float | DataPointKey]]:
    graph_rows_sorted = list(sorted(graph_rows, key=self._get_percent_adopt))
    # If no trial_data is present for a selection, value can be None
    # For example, if no stubs are selected to adopt, the graph for adopting
    # stub ASes will have no data points
    # This is proper, rather than defaulting to 0 or 100, which causes problems
    return [x for x in graph_rows_sorted if x["value"] is not None]


def _get_percent_adopt(self, graph_row: dict[str, float | DataPointKey]) -> float:
    """Extractions percent adoption for sort comparison

    Need separate function for mypy puposes
    Used in _generate_graph
    """

    percent_adopt = graph_row["data_point_key"].percent_adopt
    assert isinstance(percent_adopt, (float, SpecialPercentAdoptions))
    return float(percent_adopt)


def _get_xs(
    self, graph_rows_sorted: list[dict[str, float | DataPointKey]], line_info: LineInfo
) -> list[float]:
    """Gets the xs for a given line"""

    if line_info.hardcoded_xs:
        return line_info.hardcoded_xs
    else:
        return [
            float(x["data_point_key"].percent_adopt) * 100 for x in graph_rows_sorted
        ]


def _get_ys(
    self, graph_rows_sorted: list[dict[str, float | DataPointKey]], line_info: LineInfo
) -> list[float]:
    """Gets the ys for a given line"""

    default_ys = [x["value"] for x in graph_rows_sorted]
    if line_info.hardcoded_ys:
        return line_info.hardcoded_ys
    # Line is unrelated to percent adoption, average together
    elif line_info.unrelated_to_adoption:
        return [mean(default_ys)] * len(default_ys)
    else:
        return default_ys


def _get_yerrs(
    self, graph_rows_sorted: list[dict[str, float | DataPointKey]], line_info: LineInfo
) -> list[float]:
    """Gets the yerrs for a given line"""

    default_yerrs = [x["yerr"] for x in graph_rows_sorted]
    if line_info.hardcoded_yerrs:
        return line_info.hardcoded_yerrs
    # Line is unrelated to percent adoption, average together
    elif line_info.unrelated_to_adoption:
        return [mean(default_yerrs)] * len(default_yerrs)
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
