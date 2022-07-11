import cProfile
import pstats
import io

from pyinstrument import Profiler

#from lib_bgp_simulator import AttackerSuccessAdoptingEtcSubgraph
#from lib_bgp_simulator import AttackerSuccessAdoptingInputCliqueSubgraph
#from lib_bgp_simulator import AttackerSuccessAdoptingStubsAndMHSubgraph
#from lib_bgp_simulator import AttackerSuccessNonAdoptingEtcSubgraph
#from lib_bgp_simulator import AttackerSuccessNonAdoptingInputCliqueSubgraph
#from lib_bgp_simulator import AttackerSuccessNonAdoptingStubsAndMHSubgraph
from lib_bgp_simulator import ROVSimpleAS
from lib_bgp_simulator import Simulation
from lib_bgp_simulator import SubprefixHijack


long_run = False

if long_run:
    percent_adoptions = (0, 10, 20, 40, 60, 80, 100)
    num_trials = 100
else:
    percent_adoptions = (50,)
    num_trials = 1

sim = Simulation(num_trials=num_trials,
                 scenarios=[SubprefixHijack(AdoptASCls=ROVSimpleAS)],
#                 subgraphs=[AttackerSuccessAdoptingEtcSubgraph(),
#                            AttackerSuccessAdoptingInputCliqueSubgraph(),
#                            AttackerSuccessAdoptingStubsAndMHSubgraph(),
#                            AttackerSuccessNonAdoptingEtcSubgraph(),
#                            AttackerSuccessNonAdoptingInputCliqueSubgraph(),
#                            AttackerSuccessNonAdoptingStubsAndMHSubgraph()],
                 propagation_rounds=1,
                 parse_cpus=1)

profiler = Profiler()
profiler.start()
sim.run()
profiler.stop()
profiler.print()
