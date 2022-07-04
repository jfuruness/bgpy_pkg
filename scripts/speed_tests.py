import cProfile
import pstats
import io

#from lib_bgp_simulator import AttackerSuccessAdoptingEtcSubgraph
#from lib_bgp_simulator import AttackerSuccessAdoptingInputCliqueSubgraph
#from lib_bgp_simulator import AttackerSuccessAdoptingStubsAndMHSubgraph
#from lib_bgp_simulator import AttackerSuccessNonAdoptingEtcSubgraph
#from lib_bgp_simulator import AttackerSuccessNonAdoptingInputCliqueSubgraph
#from lib_bgp_simulator import AttackerSuccessNonAdoptingStubsAndMHSubgraph
from lib_bgp_simulator import ROVSimpleAS
from lib_bgp_simulator import Simulation
from lib_bgp_simulator import SubprefixHijack


long_run = True

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

pr = cProfile.Profile()
pr.enable()

sim.run()

pr.disable()

s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumtime')
ps.print_stats()

with open('test.txt', 'w') as f:
    f.write(s.getvalue())
