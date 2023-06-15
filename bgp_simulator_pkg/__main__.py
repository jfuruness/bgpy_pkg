from pathlib import Path

from .simulation_engine import ROVSimpleAS
from .simulation_framework import Simulation, SubprefixHijack, ScenarioConfig


def main():
    """Runs the defaults"""

    # Simulation for the paper
    sim = Simulation(
        percent_adoptions=(
            0.2,
            0.5,
        ),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptASCls=ROVSimpleAS),
        ),
        output_path=Path("~/Desktop/main_ex_graphs").expanduser(),
        num_trials=2,
        parse_cpus=1,
    )
    sim.run()


if __name__ == "__main__":
    main()
