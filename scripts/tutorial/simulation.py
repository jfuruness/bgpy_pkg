from multiprocessing import cpu_count
from pathlib import Path

from subprefix_hijack import SubprefixHijack
from peer_rov_policy import PeerROVPolicy
from rov_policy import ROVPolicy

from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_framework import Simulation, ScenarioConfig


def main():
    """Runs the defaults"""

    # Simulation for the paper
    sim = Simulation(
        percent_adoptions=(
            SpecialPercentAdoptions.ONLY_ONE,
            0.1,
            0.2,
            0.4,
            0.8,
            0.99 # SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=ROVPolicy),
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=PeerROVPolicy),
        ),
        output_dir=Path("~/Desktop/tutorial_ex").expanduser(),
        num_trials=100,
        parse_cpus=cpu_count(),
    )
    sim.run()


if __name__ == "__main__":
    main()
