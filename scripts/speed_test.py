import cProfile
import io
import pstats
import time
from pathlib import Path

from frozendict import frozendict

from bgpy.shared.constants import DIRS, SINGLE_DAY_CACHE_DIR, bgpy_logger
from bgpy.shared.enums import SpecialPercentAdoptions
from bgpy.simulation_engine import ROV
from bgpy.simulation_framework import (
    ScenarioConfig,
    Simulation,
    SubprefixHijack,
)


def main():
    """Runs the defaults"""

    # Simulation for the paper
    sim = Simulation(
        percent_adoptions=(
            SpecialPercentAdoptions.ONLY_ONE,
            0.1,
            0.2,
            0.5,
            0.8,
            0.99,
            # Using only 1 AS not adopting causes extreme variance
            # SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=ROV),
        ),
        output_dir=Path("~/Desktop/speed_test").expanduser(),
        num_trials=10,
        parse_cpus=1,
        python_hash_seed=0,
        as_graph_constructor_kwargs=frozendict(
            {
                "as_graph_collector_kwargs": frozendict(
                    {
                        # dl_time: datetime(),
                        "cache_dir": SINGLE_DAY_CACHE_DIR,
                    }
                ),
                "as_graph_kwargs": frozendict(
                    {
                        # When no ASNs are stored, .9gb/core
                        # When one set of cones is stored, 1.6gb/core
                        # When both sets of cones are stored, 2.3gb/core
                        "store_customer_cone_size": False,
                        "store_customer_cone_asns": False,
                        "store_provider_cone_size": False,
                        "store_provider_cone_asns": False,
                    }
                ),
                "tsv_path": None,  # Path.home() / "Desktop" / "caida.tsv",
            }
        ),

    )
    sim.run(GraphFactoryCls=None)


if __name__ == "__main__":
    start = time.perf_counter()
    profiler = cProfile.Profile()
    profiler.enable()
    print("Must expand the list of eligable AS classes")
    main()
    print(f"{time.perf_counter() - start:.2f}s")
    # v9 Normal 61.6s
    # v8 68.53s
    # v9 again only 63.88s
    # CIBUILDWHEEL=1 pip install frozendict - 64s
    # After removing 5% info tag from announcements
    profiler.disable()

    # Create a StringIO object to capture the profiling results
    s = io.StringIO()

    # Create a Stats object with the profiling results
    sortby = 'cumtime'
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)

    # Print the profiling results to the StringIO object
    ps.print_stats()

    # Write the profiling results to a file
    with open('/home/anon/Desktop/profile_output.txt', 'w') as f:
        f.write(s.getvalue())
