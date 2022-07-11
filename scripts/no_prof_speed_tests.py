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
                 propagation_rounds=1,
                 parse_cpus=1)
sim.run()
