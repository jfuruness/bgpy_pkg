from collections import defaultdict
from pathlib import Path
import pickle

import matplotlib.pyplot as plt  # type: ignore

from .metric_tracker import MetricKey
from .utils import get_all_metric_keys


class GraphFactory:
    """Automates graphing of default graphs"""

    def __init__(self, pickle_path: Path, graph_dir: Path) -> None:
        self.pickle_path: Path = pickle_path
        with self.pickle_path.open("rb") as f:
            self.graph_rows = pickle.load(f)
        self.graph_dir: Path = graph_dir
        self.graph_dir.mkdirs(parents=True, exist_ok=True)

    def generate_graphs(self) -> None:
        """Generates default graphs"""

        # Each metric key here contains plane, as group, and outcome
        # In other words, aech type of graph
        for metric_key in get_all_metric_keys():
            for adopting in [True, False]:
                relevant_rows = list()
                for row in self.graph_rows:
                    # Get all the rows that correspond to that type of graph
                    BaseASCls = row["data_key"].scenario_config.BaseASCls
                    AdoptASCls = row["data_key"].scenario_config.AdoptASCls
                    print("hello")
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

        graph_name = (
            f"{relevant_rows[0]['data_key'].scenario_config.ScenarioCls.__name__}"
            f"_{metric_key.as_group.value}_adopting_is_{adopting}"
            f"_{metric_key.outcome.value}"
            f"_{metric_key.plane.value}.png"
        ).replace(" ", "")
        as_cls_rows_dict = defaultdict(list)
        for row in relevant_rows:
            as_cls_rows_dict[row["scenario_config"].AdoptASCls].append(row)

        fig, ax = plt.subplots()
        fig.set_dpi(150)
        # Set X and Y axis size
        plt.xlim(0, 100)
        plt.ylim(0, 100)

        # Add the data from the lines
        for as_cls, graph_rows in as_cls_rows_dict.items():
            graph_rows_sorted = list(
                sorted(graph_rows, key=lambda x: x["data_key"].percent_adopt)
            )
            ax.errorbar(
                [x["data_key"].percent_adopt for x in graph_rows_sorted],
                [x["data_key"].value for x in graph_rows_sorted],
                yerr=[x["data_key"].yerr for x in graph_rows_sorted],
                label=as_cls.name,
            )
        # Set labels
        ax.set_ylabel(f"Percent {metric_key.outcome.value}")
        ax.set_xlabel("Percent Adoption")

        # This is to avoid warnings
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels)
        plt.tight_layout()
        plt.rcParams.update({"font.size": 14, "lines.markersize": 10})
        plt.savefig(self.graph_dir / graph_name)
        # https://stackoverflow.com/a/33343289/8903959
        plt.close(fig)
