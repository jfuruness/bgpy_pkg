from pathlib import Path
from time import perf_counter

from bgpy.simulation_engine import BGPSimplePolicy

from bgpy.simulation_framework import (
    Simulation,
    ScenarioConfig,
    ValidPrefix,
)

from small_ann import SmallAnn
import cProfile
import pstats



def main():
    """Runs the defaults"""

    ############################
    # Optimized implementation #
    ############################

    sim = Simulation(
        percent_adoptions=(
            0.1,
            .5,
            .8,
        ),
        scenario_configs=(
            ScenarioConfig(
                ScenarioCls=ValidPrefix,
                AdoptPolicyCls=BGPSimplePolicy,
                AnnCls=SmallAnn,
            ),
        ),
        output_dir=Path.home() / "Desktop" / "benchmarks",
        num_trials=20,
        parse_cpus=1,
        python_hash_seed=0
    )
    start = perf_counter()
    profile = cProfile.Profile()
    profile.enable()
    sim.run(GraphFactoryCls=None)
    # Stop profiling
    profile.disable()

    print(perf_counter() - start)

    # Save profiling results
    profile_output_file = str(Path.home() / "Desktop" / "aspa_benchmarks_profile.txt")
    with open(profile_output_file, "w") as f:
        stats = pstats.Stats(profile, stream=f)
        stats.sort_stats("cumtime").print_stats()
    print(f"Profile data saved to {profile_output_file}")
    print(perf_counter() - start)



if __name__ == "__main__":
    main()
