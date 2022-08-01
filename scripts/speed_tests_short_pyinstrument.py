# import cProfile
# import pstats
# import io

from pyinstrument import Profiler

# from bgp_simulator_pkg import AttackerSuccessAdoptingEtcSubgraph
# from bgp_simulator_pkg import AttackerSuccessAdoptingInputCliqueSubgraph
# from bgp_simulator_pkg import AttackerSuccessAdoptingStubsAndMHSubgraph
# from bgp_simulator_pkg import AttackerSuccessNonAdoptingEtcSubgraph
# from bgp_simulator_pkg import AttackerSuccessNonAdoptingInputCliqueSubgraph
# from bgp_simulator_pkg import AttackerSuccessNonAdoptingStubsAndMHSubgraph
from bgp_simulator_pkg import ROVSimpleAS
from bgp_simulator_pkg import Simulation
from bgp_simulator_pkg import SubprefixHijack

long_run = False

if long_run:
    percent_adoptions = (0, 10, 20, 40, 60, 80, 100)
    num_trials = 100
else:
    percent_adoptions = (50,)
    num_trials = 1

sim = Simulation(num_trials=num_trials,
                 scenarios=[SubprefixHijack(AdoptASCls=ROVSimpleAS)],
                 propagation_rounds=1,
                 parse_cpus=1)

# Return this commented out parameter inside the init call when needed
#                 subgraphs=[AttackerSuccessAdoptingEtcSubgraph(),
#                            AttackerSuccessAdoptingInputCliqueSubgraph(),
#                            AttackerSuccessAdoptingStubsAndMHSubgraph(),
#                            AttackerSuccessNonAdoptingEtcSubgraph(),
#                            AttackerSuccessNonAdoptingInputCliqueSubgraph(),
#                            AttackerSuccessNonAdoptingStubsAndMHSubgraph()],


profiler = Profiler()
profiler.start()
sim.run()
profiler.stop()
profiler.print()
