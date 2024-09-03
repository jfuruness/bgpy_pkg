import sys
import time
from multiprocessing import cpu_count
from pathlib import Path
from typing import Iterable

from bgpy.shared.enums import ASGroups, Outcomes, Plane, SpecialPercentAdoptions
from bgpy.simulation_engine import ROV, ROVPPV1Lite, ROVPPV2Lite
from bgpy.simulation_framework import (
    NonRoutedPrefixHijack,
    NonRoutedSuperprefixPrefixHijack,
    ScenarioConfig,
    Simulation,
    SubprefixHijack,
)
from bgpy.simulation_framework.metric_tracker.metric_key import MetricKey

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
    "num_trials": 1 if "quick" in str(sys.argv) else 50,
    "parse_cpus": cpu_count() - 2,
}


ROVPP_CLASSES = (ROVPPV2Lite, ROVPPV1Lite, ROV)


# NOTE: Normally you don't need custom metric keys
# but ROV++ paper looked specifically at the edge ASes
# So I've modified this to track the edge ASes (stubs or multihomed)
# for most papers, looking at the internet as a whole is good enough
# Additionally, adding these significantly slows down the simulations,
# so best to stick to the defaults when you can
def get_rovpp_metric_keys() -> Iterable[MetricKey]:
    """Returns all possible metric key combos for ROV++

    Modified from the utils file within the sim framework"""

    for plane in [Plane.DATA]:
        for as_group in [ASGroups.ALL_WOUT_IXPS, ASGroups.STUBS_OR_MH]:
            for outcome in [x for x in Outcomes if x != Outcomes.UNDETERMINED]:
                yield MetricKey(plane=plane, as_group=as_group, outcome=outcome)


def run_fig678():
    """Runs fig6,7,8 from ROV++ paper with policies that are implemented in BGPy

    fig 6 looks at the adopting_is_any
    fig 7 looked at adopting_is_true from stubs or multihomed
    fig 8 looked at adopting_is_false from stubs or multihomed

    CAVEAT - in the ROV++ paper we simulated non-lite versions, but BGPy has only
    the recommended lite versions
    """

    sim = Simulation(
        scenario_configs=[
            ScenarioConfig(
                ScenarioCls=SubprefixHijack,
                AdoptPolicyCls=Cls,
            )
            for Cls in ROVPP_CLASSES
        ],
        output_dir=DIR / "fig678",
        metric_keys=tuple(list(get_rovpp_metric_keys())),
        **default_kwargs,  # type: ignore
    )
    sim.run()


def run_fig9():
    """Runs fig9 from ROV++ paper with policies that are implemented in BGPy

    for this fig, adopting_is_False, and from stubs or multihomed

    CAVEAT - in the ROV++ paper we simulated non-lite versions, but BGPy has only
    the recommended lite versions
    """

    sim = Simulation(
        scenario_configs=[
            ScenarioConfig(
                ScenarioCls=NonRoutedPrefixHijack,
                AdoptPolicyCls=Cls,
            )
            for Cls in ROVPP_CLASSES
        ],
        output_dir=DIR / "fig9",
        metric_keys=tuple(list(get_rovpp_metric_keys())),
        **default_kwargs,  # type: ignore
    )
    sim.run()


def run_fig10():
    """Runs fig10 from ROV++ paper with policies that are implemented in BGPy

    for this fig, adopting_is_False, and from stubs or multihomed

    CAVEAT - in the ROV++ paper we simulated non-lite versions, but BGPy has only
    the recommended lite versions
    """

    sim = Simulation(
        scenario_configs=[
            ScenarioConfig(
                ScenarioCls=NonRoutedSuperprefixPrefixHijack,
                AdoptPolicyCls=Cls,
            )
            for Cls in ROVPP_CLASSES
        ],
        output_dir=DIR / "fig10",
        metric_keys=tuple(list(get_rovpp_metric_keys())),
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
    print(
        "NOTE: this is only running with 10 trials. Increase # of trials for more precision"
    )
    start = time.perf_counter()
    main()
    print(f"{time.perf_counter() - start}s for all sims")
