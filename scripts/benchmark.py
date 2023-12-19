from pathlib import Path

from bgpy.simulation_engine.policies.rov import ROVSimplePolicy
from bgpy.simulation_framework import Simulation, SubprefixHijack, ScenarioConfig


def main():
    """Runs the defaults"""

    # Simulation for the paper
    sim = Simulation(
        percent_adoptions=(0.1, 0.2, 0.5, 0.8),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=ROVSimplePolicy),
        ),
        output_dir=Path("~/Desktop/benchmark").expanduser(),
        num_trials=5,
        parse_cpus=1,
        python_hash_seed=0,
    )
    sim._get_data()


if __name__ == "__main__":
    main()
