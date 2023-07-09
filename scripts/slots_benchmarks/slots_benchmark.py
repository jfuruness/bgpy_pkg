import cProfile  # noqa
from multiprocessing import cpu_count  # noqa
from pathlib import Path
import pstats  # noqa
import time
import pyprof2calltree

from bgpy import SpecialPercentAdoptions
from bgpy import ROVSimpleAS
from bgpy import Simulation, SubprefixHijack, ScenarioConfig


def main():
    """Runs the defaults"""

    assert False, "Turn asserts off! (With -O flag)"

    # Simulation for the paper
    sim = Simulation(  # type: ignore
        percent_adoptions=(
            SpecialPercentAdoptions.ONLY_ONE,
            0.1,
            0.2,
            0.4,
            0.8,
            SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptASCls=ROVSimpleAS),
        ),
        output_dir=Path("~/Desktop/slots_benchmark_graphs").expanduser(),
        num_trials=10,
        parse_cpus=1,  # cpu_count(),
        python_hash_seed=1,
    )
    profiler = cProfile.Profile()
    profiler.enable()
    start = time.perf_counter()
    sim.run()
    print(time.perf_counter() - start)
    profiler.disable()

    output_file = "/tmp/profile_stats.txt"
    with open(output_file, "w") as f:
        stats = pstats.Stats(profiler, stream=f)
        stats.sort_stats("cumtime")
        stats.print_stats()

    print(f"Profiling statistics saved to {output_file}")

    callgrind_output_file = "/tmp/profile_stats.callgrind"
    with open(callgrind_output_file, "w") as f:
        pyprof2calltree.convert(stats, f)


if __name__ == "__main__":
    main()
