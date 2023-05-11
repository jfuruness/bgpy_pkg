from pathlib import Path

from .enums import SpecialPercentAdoptions
from .simulation_engine import ROVSimpleAS
from .simulation_framework import Simulation, SubprefixHijack


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
        scenarios=(SubprefixHijack(AdoptASCls=ROVSimpleAS),),
        output_path=Path("~/Desktop/graphs").expanduser(),
        num_trials=100,
        parse_cpus=12,
    )
    sim.run()


if __name__ == "__main__":
    main()
