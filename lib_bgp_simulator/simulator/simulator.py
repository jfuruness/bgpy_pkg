from multiprocessing import cpu_count
import os
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
import sys

from lib_caida_collector import CaidaCollector


from .graph import Graph
from .mp_method import MPMethod
from ..engine import BGPAS
from ..engine import ROVAS
from ..engine_input import SubprefixHijack

try:
    import ray
# pypy does not support ray, but python does
except ModuleNotFoundError:
    pass


class Simulator:
    """Runs simulations for BGP attack/defend scenarios"""

    def __init__(self, parse_cpus=cpu_count()):
        self.parse_cpus = parse_cpus

    def run(self,
            graphs=[Graph(percent_adoptions=[0, 5, 10, 20, 30, 60, 80, 100],
                          adopt_as_classes=[ROVAS],
                          EngineInputCls=SubprefixHijack,
                          num_trials=1,
                          BaseASCls=BGPAS)],
            graph_path=Path("/tmp/graphs.tar.gz"),
            assert_pypy=False,
            mp_method=MPMethod.SINGLE_PROCESS,
            ):
        """Downloads relationship data, runs simulation"""

        assert len(graphs) == 1, "Can't do more than 1 graph at once yet"
        self._validate_inputs(graph_path, assert_pypy)

        if mp_method == MPMethod.RAY:
            self._init_ray()

        # Done here so that the caida files are cached
        # So that multiprocessing doesn't interfere with one another
        CaidaCollector().run()
        self._run_and_write_graphs(graphs, mp_method, graph_path)

        if mp_method == MPMethod.RAY:
            ray.shutdown()

    def _validate_inputs(self, graph_path, assert_pypy):
        assert "pypy" in sys.executable or not assert_pypy, "Not running pypy"

        msg = (f"Change {graph_path} to Path({graph_path}) "
               "and use: from pathlib import Path")
        assert isinstance(graph_path, Path), msg

    def _init_ray(self):
        assert "pypy" not in sys.executable, "Pypy does not support ray"

        # Run with ray
        try:
            # https://github.com/ray-project/tutorial/issues/67
            ray.init(address='auto',
                     _redis_password='5241590000000000',
                     ignore_reinit_error=True)
        # If external cluster isn't running, run on local machine
        except ConnectionError as e:
            print(e)
            ray.init(ignore_reinit_error=True)

    def _run_and_write_graphs(self, graphs, mp_method, graph_path):
        self._run_graphs(graphs, mp_method)
        with TemporaryDirectory() as tmp_dir:
            graph_dir = Path(str(tmp_dir))
            self._write_graphs(graphs, graph_dir)
            self._tar_graphs(graphs, graph_dir, graph_path)

    def _run_graphs(self, graphs, mp_method):
        for graph in graphs:
            graph.run(self.parse_cpus,
                      mp_method=mp_method)

    def _write_graphs(self, graphs, graph_dir):
        for graph in graphs:
            graph.aggregate_and_write(graph_dir, self)

    def _tar_graphs(self, graphs, graph_dir, graph_path):
        with tarfile.open(graph_path, "w:gz") as tar:
            tar.add(str(graph_dir),
                    arcname=os.path.basename(str(graph_dir)))
        print(f"Wrote graphs to {graph_path}")
