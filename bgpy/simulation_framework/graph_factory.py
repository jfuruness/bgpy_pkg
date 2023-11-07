from collections import defaultdict
from functools import cached_property
import gc
from itertools import product
from pathlib import Path
import pickle

import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
from tqdm import tqdm

from .metric_tracker.metric_key import MetricKey
from .utils import get_all_metric_keys

from bgpy.enums import SpecialPercentAdoptions


class GraphFactory:
    """Automates graphing of default graphs"""

    def __init__(
        self,
        pickle_path: Path,
        graph_dir: Path,
        # A nice way to substitute labels post run
        label_replacement_dict=None,
        y_axis_label_replacement_dict=None,
        x_axis_label_replacement_dict=None,
    ) -> None:
        self.pickle_path: Path = pickle_path
        with self.pickle_path.open("rb") as f:
            self.graph_rows = pickle.load(f)
        self.graph_dir: Path = graph_dir
        self.graph_dir.mkdir(parents=True, exist_ok=True)

        if label_replacement_dict is None:
            label_replacement_dict = dict()
        self.label_replacement_dict = label_replacement_dict

        if x_axis_label_replacement_dict is None:
            x_axis_label_replacement_dict = dict()
        self.x_axis_label_replacement_dict = x_axis_label_replacement_dict

        if y_axis_label_replacement_dict is None:
            y_axis_label_replacement_dict = dict()
        self.y_axis_label_replacement_dict = y_axis_label_replacement_dict

    def generate_graphs(self) -> None:
        """Generates default graphs"""

        # Each metric key here contains plane, as group, and outcome
        # In other words, aech type of graph

        graph_infos = list(product(get_all_metric_keys(), [True, False]))

        for metric_key, adopting in tqdm(
            graph_infos, total=len(graph_infos), desc="Writing Graphs"
        ):
            relevant_rows = list()
            for row in self.graph_rows:
                # Get all the rows that correspond to that type of graph
                BaseASCls = row["data_key"].scenario_config.BaseASCls
                AdoptASCls = row["data_key"].scenario_config.AdoptASCls
                if (
                    row["metric_key"].plane == metric_key.plane
                    and row["metric_key"].as_group == metric_key.as_group
                    and row["metric_key"].outcome == metric_key.outcome
                    and (
                        (row["metric_key"].ASCls == BaseASCls and not adopting)
                        or (row["metric_key"].ASCls == AdoptASCls and adopting)
                    )
                ):
                    relevant_rows.append(row)
            self._generate_graph(metric_key, relevant_rows, adopting=adopting)

    def _generate_graph(self, metric_key: MetricKey, relevant_rows, adopting) -> None:
        """Writes a graph to the graph dir"""

        # Row is:
        # data_key: DataKey
        #    propagation_round
        #    percent_adopt
        #    scenario_config
        # metric_key: MetricKey
        #     Plane
        #     as_group
        #     outcome
        #     ASCls
        # Value: float
        # Yerr: yerr

        if not relevant_rows:
            return
        graph_name = (
            f"{relevant_rows[0]['data_key'].scenario_config.ScenarioCls.__name__}"
            f"/{metric_key.as_group.value}_adopting_is_{adopting}"
            f"/{metric_key.outcome.name}"
            f"_{metric_key.plane.value}.png"
        ).replace(" ", "")
        as_cls_rows_dict = defaultdict(list)
        for row in relevant_rows:
            as_cls_rows_dict[row["data_key"].scenario_config.AdoptASCls].append(row)

        matplotlib.use("Agg")
        fig, ax = plt.subplots()
        fig.set_dpi(150)
        # Set X and Y axis size
        plt.xlim(0, 100)
        plt.ylim(0, 100)

        def get_percent_adopt(graph_row) -> float:
            """Extractions percent adoption for sort comparison

            Need separate function for mypy puposes
            """

            percent_adopt = graph_row["data_key"].percent_adopt
            assert isinstance(percent_adopt, (float, SpecialPercentAdoptions))
            return float(percent_adopt)

        # Add the data from the lines
        for i, (as_cls, graph_rows) in enumerate(as_cls_rows_dict.items()):
            graph_rows_sorted = list(sorted(graph_rows, key=get_percent_adopt))
            ax.errorbar(
                [float(x["data_key"].percent_adopt) * 100 for x in graph_rows_sorted],
                [x["value"] for x in graph_rows_sorted],
                yerr=[x["yerr"] for x in graph_rows_sorted],
                label=self.label_replacement_dict.get(as_cls.name, as_cls.name),
                ls=self.line_styles[i],
                marker=self.markers[i],
            )
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

        # This is to avoid warnings
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels)
        plt.tight_layout()
        plt.rcParams.update({"font.size": 14, "lines.markersize": 10})
        (self.graph_dir / graph_name).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(self.graph_dir / graph_name)
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

    @cached_property
    def markers(self) -> tuple[str, ...]:
        # Leaving this as a list here for mypy
        markers = [".", "1", "*", "x", "d", "2", "3", "4"]
        markers += markers.copy()[0:-2:2]
        markers += markers.copy()[::-1]
        return tuple(markers)

    @cached_property
    def line_styles(self) -> tuple[str, ...]:
        # Leaving this as a list here for mypy
        styles = ["-", "--", "-.", ":", "solid", "dotted", "dashdot", "dashed"]
        styles += styles.copy()[::-1]
        styles += styles.copy()[0:-2:2]
        return tuple(styles)
