from multiprocessing import cpu_count
from pathlib import Path

from subprefix_hijack import SubprefixHijack
from peer_rov_as import PeerROVAS
from rov_as import ROVAS

from bgpy import Simulation, ScenarioConfig, SpecialPercentAdoptions


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
            SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptASCls=ROVAS),
            ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptASCls=PeerROVAS),
        ),
        output_dir=Path("~/Desktop/tutorial_ex").expanduser(),
        num_trials=100,
        parse_cpus=cpu_count(),
    )
    sim.run()


if __name__ == "__main__":
    main()
