from pathlib import Path

from .simulation_engine import ROVSimplePolicy
from .enums import SpecialPercentAdoptions
from .simulation_framework import Simulation, SubprefixHijack, ScenarioConfig


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
            SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=ROVSimplePolicy),
        ),
        output_dir=Path("~/Desktop/main_ex").expanduser(),
        num_trials=10,
        parse_cpus=10,
    )
    sim.run()


if __name__ == "__main__":
    main()
