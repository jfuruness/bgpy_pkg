from pathlib import Path

from bgpy import SpecialPercentAdoptions

# from bgpy import ROVSimpleAS, RealPeerROVSimpleAS
from bgpy import Simulation  # , SubprefixHijack


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
        # scenarios=(
        #     SubprefixHijack(AdoptASCls=ROVSimpleAS),
        #     SubprefixHijack(AdoptASCls=PeerROVSimpleAS),
        # ),
        output_path=Path("~/Desktop/paper_graphs").expanduser(),
        num_trials=1000,
        parse_cpus=12,
    )
    sim.run()


if __name__ == "__main__":
    main()
