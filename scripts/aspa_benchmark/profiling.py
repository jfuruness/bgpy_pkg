import cProfile
import pstats
from pathlib import Path
from time import perf_counter

from bgpy.simulation_engine import ROVSimplePolicy
from bgpy.simulation_engine import ASPASimplePolicy
from bgpy.enums import SpecialPercentAdoptions

from aspv_announcement import ASPVAnnouncement
from aspv_simple_policy import ASPVSimplePolicy
from bgpy.simulation_framework import (
    Simulation,
    SubprefixHijack,
    ScenarioConfig,
)

assert False, "Turn asserts off with pypy3 -O for benchmarks"

def main():
    """Runs the defaults"""

    output_dir = Path.home() / "Desktop" / "aspa_benchmarks"

    # Testing native BGPy implementation
    sim = Simulation(
        percent_adoptions=(
            0.1,
        ),
        scenario_configs=(
            ScenarioConfig(
                ScenarioCls=SubprefixHijack,
                AdoptPolicyCls=ASPASimplePolicy,
            ),
        ),
        output_dir=output_dir,
        num_trials=5,
        parse_cpus=1,
    )
    start = perf_counter()
    # Passing in GraphFactoryCls=None to avoid graphing
    profile = cProfile.Profile()
    profile.enable()
    sim.run(GraphFactoryCls=None)
    # Stop profiling
    profile.disable()

    # Save profiling results
    profile_output_file = str(Path.home() / "Desktop" / "aspa_benchmarks_profile.txt")
    with open(profile_output_file, "w") as f:
        stats = pstats.Stats(profile, stream=f)
        stats.sort_stats("cumtime").print_stats()
    print(f"Profile data saved to {profile_output_file}")
    print(perf_counter() - start)


if __name__ == "__main__":
    main()
