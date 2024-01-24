from pathlib import Path

from bgpy.simulation_engine import ROVSimplePolicy
from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_framework import (
    Simulation,
    SubprefixHijack,
    ScenarioConfig,
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
            # Having only one AS not adopting results in some large variance
            #.99 is a better approximation
            .99  # SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=ROVSimplePolicy),
        ),
        output_dir=Path("~/Desktop/main_ex").expanduser(),
        num_trials=1,
        parse_cpus=1,
    )
    sim.run()


if __name__ == "__main__":
    main()
