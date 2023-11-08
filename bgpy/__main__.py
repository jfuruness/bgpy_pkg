from pathlib import Path

from .simulation_engine import ROVSimpleAS
from .simulation_framework import Simulation, SubprefixHijack, ScenarioConfig


def main():
    """Runs the defaults"""

    # Simulation for the paper
    sim = Simulation(
        percent_adoptions=(0.1, 0.2, 0.5, 0.8),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptASCls=ROVSimpleAS),
        ),
        output_dir=Path("~/Desktop/main_ex").expanduser(),
        num_trials=100,
        parse_cpus=10,
    )
    sim.run()


if __name__ == "__main__":
    main()
