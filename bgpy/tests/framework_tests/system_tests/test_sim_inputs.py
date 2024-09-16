from pathlib import Path

import pytest

from bgpy.simulation_engine import BGP, ROV
from bgpy.simulation_framework import ScenarioConfig, Simulation, SubprefixHijack


@pytest.mark.slow
@pytest.mark.framework
def test_sim_inputs(tmp_path: Path):
    """Does a full run of the simulation framework

    I do my best to keep this short, since if it's too long we just don't run it
    """

    sim = Simulation(
        percent_adoptions=(0.5,),
        scenario_configs=(
            ScenarioConfig(
                ScenarioCls=SubprefixHijack,
                AdoptPolicyCls=ROV,
                BasePolicyCls=BGP,
                num_attackers=1,
            ),
        ),
        num_trials=1,
        output_dir=tmp_path / "test_sim_inputs",
        parse_cpus=1,
    )
    sim.run()
