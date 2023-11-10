from multiprocessing import cpu_count
from pathlib import Path

from subprefix_hijack import SubprefixHijack
from peer_rov_as import PeerROVAS
from rov_as import ROVAS

from bgpy import Simulation, ScenarioConfig


def main():
    """Runs the defaults"""

    # Simulation for the paper
    sim = Simulation(
        percent_adoptions=(
            # NOTE: There is currently a slight issue with the SpecialPercentAdoptions
            # SpecialPercentAdoptions.ONLY_ONE,
            .01,
            0.1,
            0.2,
            0.4,
            0.8,
            .99
            # SpecialPercentAdoptions.ALL_BUT_ONE,
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
