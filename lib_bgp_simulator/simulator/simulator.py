import os
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
import sys

from lib_caida_collector import CaidaCollector


from .graph import Graph
from ..engine import BGPAS
from ..engine import ROVAS
from ..engine_input import SubprefixHijack


class Simulator:
    """Runs simulations for BGP attack/defend scenarios"""

    def __init__(self, parse_cpus=1):
        """Saves the amount of parse cpus for multiprocessing"""

        self.parse_cpus = parse_cpus

    def run(self,
            graphs=[Graph(percent_adoptions=[0, 5, 10, 20, 30, 60, 80, 100],
                          adopt_as_classes=[ROVAS],
                          EngineInputCls=SubprefixHijack,
                          num_trials=1,
                          BaseASCls=BGPAS)],
            graph_path=Path("/tmp/graphs.tar.gz"),
            assert_pypy=False,
            ):
        """Downloads relationship data, runs simulation

        Graphs -> A list of graph classes
        graph_path: Where to store the graphs. Should be a .tar.gz file
        assert_pypy: Ensures you are using pypy if true
        mp_method: Multiprocessing method
        """

        assert len(graphs) == 1, "Can't do more than 1 graph at once yet"
        self._validate_inputs(graph_path, assert_pypy)

        # Done here so that the caida files are cached
        # So that multiprocessing doesn't interfere with one another
        CaidaCollector().run()
        # Runs trials and writes graphs
        self._run_and_write_graphs(graphs, graph_path)

    def _validate_inputs(self, graph_path, assert_pypy):
        """Validates inputs"""

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

    def _run_graphs(self, graphs, mp_method):
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
