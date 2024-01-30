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

    output_dir_parent = Path.home() / "Desktop" / "aspa_benchmarks"

    # Testing native BGPy implementation
    sim = Simulation(
        percent_adoptions=(
            SpecialPercentAdoptions.ONLY_ONE,
            0.1,
            0.2,
            0.5,
            0.8,
            SpecialPercentAdoptions.ALL_BUT_ONE,
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
    sim.run(GraphFactoryCls=None)
    print(perf_counter() - start)



    # Simulation for the paper
    sim = Simulation(
        percent_adoptions=(
            SpecialPercentAdoptions.ONLY_ONE,
            0.1,
            0.2,
            0.5,
            0.8,
            SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        scenario_configs=(
            ScenarioConfig(
                ScenarioCls=SubprefixHijack,
                AdoptPolicyCls=ASPVSimplePolicy,
                AnnCls=ASPVAnnouncement
            ),
        ),
        output_dir=output_dir,
        num_trials=5,
        parse_cpus=1,
    )
    start = perf_counter()
    # Passing in GraphFactoryCls=None to avoid graphing
    sim.run(GraphFactoryCls=None)
    print(perf_counter() - start)


if __name__ == "__main__":
    main()
