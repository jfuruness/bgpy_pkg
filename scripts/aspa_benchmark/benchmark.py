from pathlib import Path
from time import perf_counter

from bgpy.simulation_engine import ASPASimplePolicy
from bgpy.enums import SpecialPercentAdoptions

from aspv_announcement import ASPVAnnouncement
from aspv_announcement_small import SmallASPVAnn
from aspv_simple_policy import ASPVSimplePolicy
from small_ann import SmallAnn
from bgpy.simulation_framework import (
    Simulation,
    AccidentalRouteLeak,
    ScenarioConfig,
)

assert False, "Turn asserts off with pypy3 -O for benchmarks"


def main():
    """Runs the defaults"""

    output_dir = Path.home() / "Desktop" / "aspa_benchmarks"

    # Testing native BGPy implementation
    sim = Simulation(
        propagation_rounds=2,  # required for RouteLeak
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
                ScenarioCls=AccidentalRouteLeak,
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
    print("Native BGPy implementation", str(perf_counter() - start))

    # Testing native BGPy with small ann
    sim = Simulation(
        propagation_rounds=2,  # required for RouteLeak
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
                ScenarioCls=AccidentalRouteLeak,
                AdoptPolicyCls=ASPASimplePolicy,
                AnnCls=SmallAnn,
            ),
        ),
        output_dir=output_dir,
        num_trials=5,
        parse_cpus=1,
    )
    start = perf_counter()
    # Passing in GraphFactoryCls=None to avoid graphing
    sim.run(GraphFactoryCls=None)
    print("Native BGPy with SmallAnn", str(perf_counter() - start))

    # Testing Joel's default
    sim = Simulation(
        propagation_rounds=2,  # required for RouteLeak
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
                ScenarioCls=AccidentalRouteLeak,
                AdoptPolicyCls=ASPVSimplePolicy,
                AnnCls=ASPVAnnouncement,
            ),
        ),
        output_dir=output_dir,
        num_trials=5,
        parse_cpus=1,
    )
    start = perf_counter()
    # Passing in GraphFactoryCls=None to avoid graphing
    sim.run(GraphFactoryCls=None)
    print("Joel's implementation", str(perf_counter() - start))

    # Testing Joel's with a small announcement
    sim = Simulation(
        propagation_rounds=2,  # required for RouteLeak
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
                ScenarioCls=AccidentalRouteLeak,
                AdoptPolicyCls=ASPVSimplePolicy,
                AnnCls=SmallASPVAnn,
            ),
        ),
        output_dir=output_dir,
        num_trials=5,
        parse_cpus=1,
    )
    start = perf_counter()
    # Passing in GraphFactoryCls=None to avoid graphing
    sim.run(GraphFactoryCls=None)
    print("Joel's implementation with SmallASPVAnn", str(perf_counter() - start))


if __name__ == "__main__":
    main()
