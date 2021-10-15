import logging
import os
from pathlib import Path
import tarfile
import sys

from tqdm import tqdm

from lib_caida_collector import CaidaCollector
from lib_utils.base_classes import Base


from .graph import Graph
from .mp import MP
from ..engine import BGPAS
from ..engine import ROVAS
from ..engine import SimulatorEngine
from ..engine_input import SubprefixHijack


class Simulator(Base):
    """Runs simulations for BGP attack/defend scenarios"""

    def run(self,
            graphs=[Graph(percent_adoptions=[0, 5,10,20,30,40,60,80,100],
                          adopt_as_classes=[ROVAS],
                          EngineInputCls=SubprefixHijack,
                          num_trials=1,
                          BaseASCls=BGPAS)],
            graph_path=Path("/tmp/graphs.tar.gz"),
            assert_pypy=False,
            mp_method=MP.SINGLE_PROCESS,
            ):
        """Downloads relationship data, runs simulation"""
        assert "pypy" in sys.executable or not assert_pypy, "Not running pypy"

        msg = (f"Change {graph_path} to Path({graph_path}) "
                "and use: from pathlib import Path")
        assert isinstance(graph_path, Path), msg

        # https://stackoverflow.com/a/51996829/8903959
        if "pypy" not in sys.executable:
            import ray
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


        # Done here so that the caida files are cached
        # So that multiprocessing doesn't interfere with one another
        CaidaCollector(_dir=self.base_dir).read_file()

        total = sum(x.total_scenarios for x in graphs)
        for graph in graphs:
            graph.run(self.parse_cpus,
                      self._dir,
                      caida_dir=self.base_dir,
                      mp_method=mp_method)
        for graph in graphs:
            graph.aggregate_and_write(self._dir, self)

        with tarfile.open(graph_path, "w:gz") as tar:
            tar.add(str(self._dir),
                    arcname=os.path.basename(str(self._dir)))
        print(f"Wrote graphs to {graph_path}")
        if "pypy" not in sys.executable:
            ray.shutdown()
        return graphs



