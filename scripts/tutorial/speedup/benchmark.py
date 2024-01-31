from pathlib import Path
from time import perf_counter

from bgpy.simulation_engine import BGPSimplePolicy

from bgpy.simulation_framework import (
    Simulation,
    ScenarioConfig,
    ValidPrefix,
)

from small_ann import SmallAnn


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
                AdoptPolicyCls=BGPSimplePolicy,
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
                AdoptPolicyCls=BGPSimplePolicy,
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


if __name__ == "__main__":
    main()
