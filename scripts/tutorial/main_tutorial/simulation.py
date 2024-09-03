from multiprocessing import cpu_count
from pathlib import Path

from peer_rov import PeerROV
from rov import ROV
from subprefix_hijack import SubprefixHijack

from bgpy.shared.enums import SpecialPercentAdoptions
from bgpy.simulation_framework import ScenarioConfig, Simulation


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
            0.99,  # SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=ROV),
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=PeerROV),
        ),
        output_dir=Path("~/Desktop/tutorial_ex").expanduser(),
        num_trials=100,
        parse_cpus=cpu_count(),
    )
    sim.run()


if __name__ == "__main__":
    print("This takes about 6 minutes with PyPy")
    main()
