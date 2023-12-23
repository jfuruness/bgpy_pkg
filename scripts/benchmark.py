from pathlib import Path

from bgpy.simulation_engines.py_simulation_engine.policies.rov import ROVSimplePolicy
from bgpy.simulation_frameworks.py_simulation_framework import PySimulation, SubprefixHijack, ScenarioConfig


def main():
    """Runs the defaults"""

    # Simulation for the paper
    sim = PySimulation(
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
