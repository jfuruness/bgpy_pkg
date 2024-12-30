from pathlib import Path

from bgpy.shared.enums import SpecialPercentAdoptions
from bgpy.simulation_engine import ASRA, ASPAwN
from bgpy.simulation_framework import ScenarioConfig, Simulation, ForgedOriginPrefixHijack


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
            ScenarioConfig(ScenarioCls=ForgedOriginPrefixHijack, AdoptPolicyCls=ASRA),
            ScenarioConfig(ScenarioCls=ForgedOriginPrefixHijack, AdoptPolicyCls=ASPAwN),
        ),
        output_dir=Path("~/Desktop/aspawn").expanduser(),
        num_trials=10,
        parse_cpus=10,
    )
    sim.run()


if __name__ == "__main__":
    main()
