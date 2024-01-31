from multiprocessing import cpu_count
from pathlib import Path
import time

from bgpy.simulation_engine import (
    ASPASimplePolicy,
    BGPSecSimplePolicy,
    PathendSimplePolicy,
    OnlyToCustomersSimplePolicy,
)

from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_framework import (
    Simulation,
    AccidentalRouteLeak,
    PrefixHijack,
    preprocess_anns_funcs,
    ScenarioConfig,
)

default_kwargs = {
    "percent_adoptions": (
        SpecialPercentAdoptions.ONLY_ONE,
        0.1,
        0.2,
        0.5,
        0.8,
        0.99,
        # Using only 1 AS not adopting causes extreme variance
        # SpecialPercentAdoptions.ALL_BUT_ONE,
    ),
    "num_trials": 20,
    "parse_cpus": cpu_count(),
}

classes = [
    ASPASimplePolicy,
    BGPSecSimplePolicy,
    PathendSimplePolicy,
    OnlyToCustomersSimplePolicy,
]


def main():
    """Runs the defaults"""

    DIR = Path.home() / "Desktop" / "aspa_sims"

    # Route leak
    sim = Simulation(
        scenario_configs=tuple(
            [
                ScenarioConfig(
                    ScenarioCls=AccidentalRouteLeak, AdoptPolicyCls=AdoptPolicyCls
                )
                for AdoptPolicyCls in classes
            ]
        ),
        propagation_rounds=2,
        output_dir=DIR / "accidental_route_leak",
        **default_kwargs,
    )
    start = time.perf_counter()
    sim.run()
    print(time.perf_counter() - start)

    # Origin Hijack
    sim = Simulation(
        scenario_configs=tuple(
            [
                ScenarioConfig(
                    ScenarioCls=PrefixHijack,
                    AdoptPolicyCls=AdoptPolicyCls,
                    preprocess_anns_func=preprocess_anns_funcs.origin_hijack,
                )
                for AdoptPolicyCls in classes
            ]
        ),
        output_dir=DIR / "origin_hijack",
        **default_kwargs,
    )
    start = time.perf_counter()
    sim.run()
    print(time.perf_counter() - start)

    # Origin Spoofing Hijack
    sim = Simulation(
        scenario_configs=tuple(
            [
                ScenarioConfig(
                    ScenarioCls=PrefixHijack,
                    AdoptPolicyCls=AdoptPolicyCls,
                    preprocess_anns_func=preprocess_anns_funcs.origin_spoofing_hijack,
                )
                for AdoptPolicyCls in classes
            ]
        ),
        output_dir=DIR / "origin_spoofing",
        **default_kwargs,
    )
    start = time.perf_counter()
    sim.run()
    print(time.perf_counter() - start)

    # Shortest path export all
    sim = Simulation(
        scenario_configs=tuple(
            [
                ScenarioConfig(
                    ScenarioCls=PrefixHijack,
                    AdoptPolicyCls=AdoptPolicyCls,
                    preprocess_anns_func=(
                        preprocess_anns_funcs.shortest_path_export_all_hijack
                    ),
                )
                for AdoptPolicyCls in classes
            ]
        ),
        output_dir=DIR / "shortest_path_export_all",
        **default_kwargs,
    )
    start = time.perf_counter()
    sim.run()
    print(time.perf_counter() - start)

    # Shortest path export all multi attackers
    sim = Simulation(
        scenario_configs=tuple(
            [
                ScenarioConfig(
                    ScenarioCls=PrefixHijack,
                    AdoptPolicyCls=AdoptPolicyCls,
                    preprocess_anns_func=(
                        preprocess_anns_funcs.shortest_path_export_all_hijack
                    ),
                    num_attackers=10,
                )
                for AdoptPolicyCls in classes
            ]
        ),
        output_dir=DIR / "shortest_path_export_all_multi",
        **default_kwargs,
    )
    start = time.perf_counter()
    sim.run()
    print(time.perf_counter() - start)

    # geographic adoption
    raise NotImplementedError("GEOGRAPHIC ADOPTION")


if __name__ == "__main__":
    main()
