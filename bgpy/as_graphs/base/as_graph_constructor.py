import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from frozendict import frozendict

from bgpy.shared.constants import bgpy_logger

if TYPE_CHECKING:
    from .as_graph import ASGraph
    from .as_graph_collector import ASGraphCollector
    from .as_graph_info import ASGraphInfo


class ASGraphConstructor(ABC):
    def __init__(
        self,
        ASGraphCollectorCls: type["ASGraphCollector"],
        ASGraphCls: type["ASGraph"],
        as_graph_collector_kwargs=frozendict(),
        as_graph_kwargs=frozendict(),
        tsv_path: Path | None = None,
        stubs: bool = True,
    ) -> None:
        """Stores download time and cache_dir instance vars and creates dir"""

        self.as_graph_collector: ASGraphCollector = ASGraphCollectorCls(
            **as_graph_collector_kwargs
        )
        self.ASGraphCls: type[ASGraph] = ASGraphCls
        self.as_graph_kwargs = as_graph_kwargs
        self.tsv_path: Path | None = tsv_path
        self.stubs: bool = stubs

    def run(self) -> "ASGraph":
        """Generates AS graph in the following steps:

        1. download file from source using the GraphCollector
        2. parse downloaded file to get ASGraphInfo object
        3. Generate the graph based on ASGraphInfo object
        4. Write to tsv_path if it is set
        5. Return ASGraph
        """

        # Download file (for ex: from CAIDA)
        dl_path = self.as_graph_collector.run()
        # Get ASGraphInfo from downloaded file
        as_graph_info = self._get_as_graph_info(dl_path)
        # Generate AS Graph from ASGraphInfo
        as_graph = self._get_as_graph(as_graph_info)
        if not self.stubs:
            invalid_asns = frozenset([as_obj.asn for as_obj in as_graph if as_obj.stub])
            # Get ASGraphInfo from downloaded file
            as_graph_info = self._get_as_graph_info(dl_path, invalid_asns)
            # Generate AS Graph from ASGraphInfo
            as_graph = self._get_as_graph(as_graph_info)

        # Write to TSV if tsv_path is set
        self.write_tsv(as_graph, self.tsv_path)
        return as_graph

    def remove_stubs(self, as_graph: "ASGraph") -> None:
        """Removes stubs from as graph"""

        stubs = [as_obj for as_obj in as_graph if as_obj.stub]
        for stub in stubs:
            for provider in stub.providers:
                customers = tuple([x for x in provider.customers if x.asn != stub.asn])
                provider.customers = customers

    @staticmethod
    def write_tsv(as_graph: "ASGraph", tsv_path: Path | None = None) -> None:
        """Writes AS Graph to TSV"""

        if tsv_path:
            bgpy_logger.info(
                f"Writing as graph to {tsv_path} "
                "if you want to save time and not do this, pass tsv_path=None "
                "to the run function"
            )

            with tsv_path.open(mode="w") as f:
                # Get columns
                cols: list[str] = list(
                    next(iter(as_graph.as_dict.values())).db_row.keys()
                )
                writer = csv.DictWriter(f, fieldnames=cols, delimiter="\t")
                writer.writeheader()
                for x in as_graph.as_dict.values():
                    writer.writerow(x.db_row)

    @abstractmethod
    def _get_as_graph_info(
        self, dl_path: Path, invalid_asns: frozenset[int] = frozenset()
    ) -> "ASGraphInfo":
        """Reads cached directory, gets AS graph info and returns ASGraphInfo

        dl_path is the Path to the downloaded file
        """
        raise NotImplementedError

    @abstractmethod
    def _get_as_graph(self, as_graph_info: "ASGraphInfo") -> "ASGraph":
        """Returns AS Graph based on ASGraphInfo"""
        raise NotImplementedError
