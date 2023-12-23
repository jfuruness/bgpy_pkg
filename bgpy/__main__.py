from pathlib import Path

from bgpy.simulation_engines.py_simulation_engine import ROVSimplePolicy
from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_frameworks.py_simulation_framework import (
    PySimulation,
    SubprefixHijack,
    ScenarioConfig,
)


def main():
    """Runs the defaults"""

    # Simulation for the paper
    sim = PySimulation(
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
        num_trials=1,
        parse_cpus=1,
    )
    sim.run()


if __name__ == "__main__":
    main()
