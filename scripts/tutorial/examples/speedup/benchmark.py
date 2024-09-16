from pathlib import Path
from time import perf_counter

from small_ann import SmallAnn

from bgpy.simulation_engine import BGP
from bgpy.simulation_framework import (
    ScenarioConfig,
    Simulation,
    ValidPrefix,
)


def main():
    """Runs the defaults"""

    sim = Simulation(
        percent_adoptions=(
            0.1,
            0.5,
            0.8,
        ),
        scenario_configs=(
            ScenarioConfig(
                ScenarioCls=ValidPrefix,
                AdoptPolicyCls=BGP,
                AnnCls=SmallAnn,
            ),
        ),
        output_dir=Path.home() / "Desktop" / "benchmarks",
        num_trials=20,
        parse_cpus=1,
    )
    start = perf_counter()
    sim.run(GraphFactoryCls=None)
    print(perf_counter() - start)

    ############################
    # Optimized implementation #
    ############################

    sim = Simulation(
        percent_adoptions=(
            0.1,
            0.5,
            0.8,
        ),
        scenario_configs=(
            ScenarioConfig(
                ScenarioCls=ValidPrefix,
                AdoptPolicyCls=BGP,
            ),
        ),
        output_dir=Path.home() / "Desktop" / "benchmarks",
        num_trials=20,
        parse_cpus=1,
    )
    start = perf_counter()
    sim.run(GraphFactoryCls=None)
    print(perf_counter() - start)


if __name__ == "__main__":
    main()
