import os
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
import sys

from lib_caida_collector import CaidaCollector


from .graph import Graph
from .subgraphs import AttackerSuccessAdoptingEtcSubgraph
from .subgraphs import AttackerSuccessAdoptingInputCliqueSubgraph
from .subgraphs import AttackerSuccessAdoptingStubsAndMHSubgraph
from .subgraphs import AttackerSuccessNonAdoptingEtcSubgraph
from .subgraphs import AttackerSuccessNonAdoptingInputCliqueSubgraph
from .subgraphs import AttackerSuccessNonAdoptingStubsAndMHSubgraph

from ..engine import BGPAS
from ..engine import ROVSimpleAS
from ..scenarios import SubprefixHijack


class Simulator:
    """Runs simulations for BGP attack/defend scenarios"""

    def __init__(self, parse_cpus=1):
        """Saves the amount of parse cpus for multiprocessing"""

        self.parse_cpus = parse_cpus

    def run(self,
            graphs=[Graph(name="test_graph",
                          percent_adoptions=(5, 10),
                          scenarios=[SubprefixHijack(AdoptASCls=x)
                                     for x in [ROVSimpleAS]],
                          subgraphs=[
                            AttackerSuccessAdoptingEtcSubgraph(),
                            AttackerSuccessAdoptingInputCliqueSubgraph(),
                            AttackerSuccessAdoptingStubsAndMHSubgraph(),
                            AttackerSuccessNonAdoptingEtcSubgraph(),
                            AttackerSuccessNonAdoptingInputCliqueSubgraph(),
                            AttackerSuccessNonAdoptingStubsAndMHSubgraph()],
                          num_trials=2,
                          propagation_rounds=1)],
            graph_path=Path("/tmp/graphs.tar.gz"),
            assert_pypy=False,
            ):
        """Downloads relationship data, runs simulation

        Graphs -> A list of graph classes
        graph_path: Where to store the graphs. Should be a .tar.gz file
        assert_pypy: Ensures you are using pypy if true
        mp_method: Multiprocessing method
        """

        self._validate_inputs(graphs, graph_path, assert_pypy)

        # Done here so that the caida files are cached
        # So that multiprocessing doesn't interfere with one another
        print("running caida (DELETE)")
        CaidaCollector().run()
        # Runs trials and writes graphs
        self._run_and_write_graphs(graphs, graph_path)

    def _validate_inputs(self, graphs, graph_path, assert_pypy):
        """Validates inputs"""

        # Ensure graph names are unique so that we can write them easily later
        graph_names = [x.name for x in graphs]
        msg = "Graphs need unique names to avoid overwriting each other"
        assert len(graph_names) == len(set(graph_names)), msg

        assert "pypy" in sys.executable or not assert_pypy, "Not running pypy"

        msg = (f"Change {graph_path} to Path({graph_path}) "
               "and use: from pathlib import Path")
        assert isinstance(graph_path, Path), msg
        assert str(graph_path).endswith(".tar.gz")

    def _run_and_write_graphs(self, graphs, graph_path):
        """Runs graphs and writes results"""

        self._run_graphs(graphs)
        # Write graphs to a tmp dir, then save to a .tar.gz
        with TemporaryDirectory() as tmp_dir:
            graph_dir = Path(str(tmp_dir))
            self._write_graphs(graphs, graph_dir)
            self._tar_graphs(graphs, graph_dir, graph_path)

    def _run_graphs(self, graphs):
        """Get data for all graphs"""

        for graph in graphs:
            graph.run(self.parse_cpus)

    def _write_graphs(self, graphs, graph_dir):
        """Aggregates and writes all graphs"""

        for graph in graphs:
            graph.aggregate_and_write(graph_dir, self)

    def _tar_graphs(self, graphs, graph_dir, graph_path):
        """Tars graphs"""

        with tarfile.open(graph_path, "w:gz") as tar:
            tar.add(str(graph_dir),
                    arcname=os.path.basename(str(graph_dir)))
        print(f"Wrote graphs to {graph_path}")
