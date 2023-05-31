from pathlib import Path

from bgp_simulator_pkg import SpecialPercentAdoptions
from bgp_simulator_pkg import ROVSimpleAS, PeerROVSimpleAS
from bgp_simulator_pkg import Simulation, SubprefixHijack


def main():
    """Runs the defaults"""

    # Simulation for the paper
    sim = Simulation(
        percent_adoptions = (
            SpecialPercentAdoptions.ONLY_ONE,
            .1,
            .2,
            .4,
            .8,
            SpecialPercentAdoptions.ALL_BUT_ONE
        ),
        scenarios=(
            SubprefixHijack(AdoptASCls=ROVSimpleAS),
            SubprefixHijack(AdoptASCls=PeerROVSimpleAS),
        ),
        output_path=Path("~/Desktop/paper_graphs").expanduser(),
        num_trials=1000,
        parse_cpus=12,
    )
    sim.run()


if __name__ == "__main__":
    main()
