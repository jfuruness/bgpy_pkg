import logging
import os
import tarfile
import sys

from tqdm import tqdm

from lib_caida_collector import CaidaCollector
from lib_utils.base_classes import Base

from .attacks import SubprefixHijack
from .graph import Graph
from ..engine import BGPAS, BGPPolicy
from ..engine import ROVPolicy
from ..engine import SimulatorEngine


class Simulator(Base):
    """Runs simulations for BGP attack/defend scenarios"""

    def run(self,
            graphs=[Graph(percent_adoptions=[0, 5,10,20,30,40,60,80,100],
                          adopt_policies=[ROVPolicy],
                          AttackCls=SubprefixHijack,
                          num_trials=1,
                          base_policy=BGPPolicy)],
            graph_path="/tmp/graphs.tar.gz",
            ):
        """Downloads relationship data, runs simulation"""

        # https://stackoverflow.com/a/51996829/8903959
        if "pypy" not in sys.executable:
            input("Not running with pypy. Press enter to continue")

        # Done here so that the caida files are cached
        # So that multiprocessing doesn't interfere with one another
        CaidaCollector(_dir=self._dir).read_file()

        total = sum(x.total_scenarios for x in graphs)
        for graph in graphs:
            graph.run(self.parse_cpus, self._dir, debug=self.debug)
        for graph in graphs:
            graph.aggregate_and_write(self._dir)

        with tarfile.open(graph_path, "w:gz") as tar:
            tar.add(self._dir, arcname=os.path.basename(self._dir))
        print(f"Wrote graphs to {graph_path}")

        return graphs
