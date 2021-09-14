import os
import tarfile

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
            BaseASCls=BGPAS,
            graphs=[Graph(percent_adoptions=[0, 5,10,20,30,40,60,80,100],
                          adopt_policies=[ROVPolicy],
                          AttackCls=SubprefixHijack,
                          num_trials=1,
                          base_policy=BGPPolicy)],
            graph_path="/tmp/graphs.tar.gz",
            ):
        """Downloads relationship data, runs simulation"""

        collector = CaidaCollector(BaseASCls=BGPAS,
                                   GraphCls=SimulatorEngine,
                                   **self.kwargs)
        base_engine = collector.run()

        total = sum(x.total_scenarios for x in graphs)
        with tqdm(total=total, desc="Running trials") as pbar:
            for graph in graphs:
                graph.run(base_engine, pbar)
        for graph in graphs:
            graph.aggregate_and_write(self._dir)

        with tarfile.open(graph_path, "w:gz") as tar:
            tar.add(self._dir, arcname=os.path.basename(self._dir))
        print(f"Wrote graphs to {graph_path}")

        return graphs
