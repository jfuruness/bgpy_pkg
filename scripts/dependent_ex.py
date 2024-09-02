from pathlib import Path

from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_engine import ROV
from bgpy.simulation_framework import (
    DependentSimulation,
    PrefixHijack,
    ScenarioConfig,
    preprocess_anns_funcs,
)


def main():
    """Runs the defaults"""

    # DependentSimulation for the paper
    sim = DependentSimulation(
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
            ScenarioConfig(
                ScenarioCls=PrefixHijack,
                AdoptPolicyCls=ROV,
                preprocess_anns_func=(
                    preprocess_anns_funcs.forged_origin_export_all_hijack
                ),
            ),
        ),
        output_dir=Path("~/Desktop/dependent_ex").expanduser(),
        num_trials=10,
        parse_cpus=10,
    )
    sim.run()


if __name__ == "__main__":
    main()
