from multiprocessing import cpu_count
from pathlib import Path
import time

from bgp_simulator_pkg import SpecialPercentAdoptions

# from bgp_simulator_pkg import ROVSimpleAS, SubprefixHijack
from bgp_simulator_pkg import Simulation


def main():
    """Runs the defaults"""
    # Simulation for the paper
    sim = Simulation(
        percent_adoptions=(
            SpecialPercentAdoptions.ONLY_ONE,
            0.1,
            0.2,
            0.4,
            0.8,
            SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        # scenario_config=(SubprefixHijack(AdoptASCls=ROVSimpleAS),),
        output_path=Path("~/Desktop/benchmark_graphs").expanduser(),
        num_trials=1000,
        parse_cpus=cpu_count(),
    )
    start = time.perf_counter()
    sim.run()
    print(time.perf_counter() - start)


if __name__ == "__main__":
    main()
