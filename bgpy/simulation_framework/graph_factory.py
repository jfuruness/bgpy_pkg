from collections import defaultdict
from itertools import product
from pathlib import Path
import pickle
from typing import Union

import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
from tqdm import tqdm

from .metric_tracker.metric_key import MetricKey
from .utils import get_all_metric_keys

from bgpy.enums import SpecialPercentAdoptions


class GraphFactory:
    """Automates graphing of default graphs"""

    def __init__(self, pickle_path: Path, graph_dir: Path) -> None:
        self.pickle_path: Path = pickle_path
        with self.pickle_path.open("rb") as f:
            self.graph_rows = pickle.load(f)
        self.graph_dir: Path = graph_dir
        self.graph_dir.mkdir(parents=True, exist_ok=True)

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
            f"_{metric_key.as_group.value}_adopting_is_{adopting}"
            f"_{metric_key.outcome.name}"
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

        def get_percent_adopt(graph_row) -> Union[float, SpecialPercentAdoptions]:
            """Extractions percent adoption for sort comparison

            Need separate function for mypy puposes
            """

            percent_adopt = graph_row["data_key"].percent_adopt
            assert isinstance(percent_adopt, (float, SpecialPercentAdoptions))
            return percent_adopt

        # Add the data from the lines
        for as_cls, graph_rows in as_cls_rows_dict.items():
            graph_rows_sorted = list(
                sorted(
                    graph_rows,
                    key=get_percent_adopt
                )
            )
            ax.errorbar(
                [x["data_key"].percent_adopt * 100 for x in graph_rows_sorted],
                [x["value"] for x in graph_rows_sorted],
                yerr=[x["yerr"] for x in graph_rows_sorted],
                label=as_cls.name,
            )
        # Set labels
        ax.set_ylabel(f"PERCENT {metric_key.outcome.name}".replace("_", " "))
        ax.set_xlabel("Percent Adoption")

        # This is to avoid warnings
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels)
        plt.tight_layout()
        plt.rcParams.update({"font.size": 14, "lines.markersize": 10})
        plt.savefig(self.graph_dir / graph_name)
        # https://stackoverflow.com/a/33343289/8903959
        plt.close(fig)
