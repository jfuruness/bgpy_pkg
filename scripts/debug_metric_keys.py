import time
from typing import Iterable
from pathlib import Path

from bgpy.shared.enums import SpecialPercentAdoptions
from bgpy.simulation_framework import (
    ScenarioConfig,
    Simulation,
    VictimsPrefix,
)
from bgpy.shared.enums import ASGroups, InAdoptingASNs, Outcomes, Plane
from bgpy.simulation_framework.graph_data_aggregator.graph_category import GraphCategory


def get_all_graph_categories() -> Iterable[GraphCategory]:
    """Returns all possible metric key combos"""

    for plane in [Plane.DATA, Plane.CTRL]:
        for as_group in [ASGroups.ALL_WOUT_IXPS, ASGroups.STUBS_OR_MH]:
            for outcome in [x for x in Outcomes if x != Outcomes.UNDETERMINED]:
                for in_adopting_asns_enum in list(InAdoptingASNs):
                    yield GraphCategory(
                        plane=plane,
                        as_group=as_group,
                        outcome=outcome,
                        in_adopting_asns=in_adopting_asns_enum,
                    )



def main():
    """Runs the defaults"""

    # Simulation for the paper
    sim = Simulation(
        percent_adoptions=(
            0.5,
        ),
        scenario_configs=(
            ScenarioConfig(ScenarioCls=VictimsPrefix),
        ),
        output_dir=Path("~/Desktop/debug").expanduser(),
        num_trials=1,
        parse_cpus=1,
        graph_categories=tuple(get_all_graph_categories()),
        control_plane_tracking=True
    )
    sim.run()


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    print(f"{time.perf_counter() - start:.2f}s")
