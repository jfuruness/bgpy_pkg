from multiprocessing import cpu_count
from pathlib import Path
import sys
import time

from bgpy.enums import ASGroups, SpecialPercentAdoptions
from bgpy.simulation_engine import ROVPPV1Lite, ROVPPV2Lite, ROV

from bgpy.simulation_framework import (
    Simulation,
    PrefixHijack,
    SubprefixHijack,
    ScenarioConfig,
)

DIR = Path.home() / "Desktop" / "rovpp_reproduction"

default_kwargs = {
    "percent_adoptions": (
            SpecialPercentAdoptions.ONLY_ONE,
            0.1,
            0.2,
            0.5,
            0.8,
            0.99,
    ),
    "num_trials": 1 if "quick" in str(sys.argv) else 1000,
    "parse_cpus": 1 if "quick" in str(sys.argv) else cpu_count() - 2,
}


ROVPP_CLASSES = (ROVPPV2Lite, ROVPPV1Lite, ROV)

def run_fig678():
    """Runs fig6,7,8 from ROV++ paper with policies that are implemented in BGPy

    fig 6 looks at the adopting_is_any
    NOTE: for fig7 and 8 we only track __all ases__ whereas fig 7 and 8
    in the paper only looked at edge ASes
    I can fix this later but due to time constraints going to leave it for now
    fig 7 looked at adopting_is_true
    fig 8 looked at adopting_is_false
    """

    sim = Simulation(
        scenario_configs=[
            ScenarioConfig(
                ScenarioCls=SubprefixHijack,
                AdoptPolicyCls=Cls,
            ) for Cls in ROVPP_CLASSES
        ],
        output_dir=DIR / "fig678",
        **default_kwargs,  # type: ignore
    )
    sim.run()


def run_fig9():
    """Runs fig9 from ROV++ paper with policies that are implemented in BGPy

    fig 9 in the paper looked at only edge ASes, leaving this difference for now
    """

    sim = Simulation(
        scenario_configs=[
            ScenarioConfig(
                ScenarioCls=NonRoutedPrefixHijack,
                AdoptPolicyCls=Cls,
            ) for Cls in ROVPP_CLASSES
        ],
        output_dir=DIR / "fig9",
        **default_kwargs,  # type: ignore
    )
    sim.run()


def run_fig10():
    """Runs fig10 from ROV++ paper with policies that are implemented in BGPy

    fig 10 in the paper looked at only edge ASes, leaving this difference for now
    """

    sim = Simulation(
        scenario_configs=[
            ScenarioConfig(
                ScenarioCls=NonRoutedSuperprefixPrefixHijack,
                AdoptPolicyCls=Cls,
            ) for Cls in ROVPP_CLASSES
        ],
        output_dir=DIR / "fig10",
        **default_kwargs,  # type: ignore
    )
    sim.run()


def main():
    """Runs the defaults"""

    sim_funcs = (run_fig678, run_fig9, run_fig10)
    for sim_func in sim_funcs:
        start = time.perf_counter()
        sim_func()  # type: ignore
        print(f"{time.perf_counter() - start}s for {getattr(sim_func, '__name__', '')}")


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    print(f"{time.perf_counter() - start}s for all sims")
