from pathlib import Path

import pytest

from bgpy.simulation_engines.py_simulation_engine import BGPSimplePolicy
from bgpy.simulation_engines.py_simulation_engine import ROVSimplePolicy
from bgpy.simulation_frameworks.py_simulation_framework import SubprefixHijack
from bgpy.simulation_frameworks.py_simulation_framework import ScenarioConfig
from bgpy.simulation_frameworks.py_simulation_framework import PySimulation


@pytest.mark.slow
@pytest.mark.framework
def test_sim_inputs(tmp_path: Path):
    """Does a full run of the simulation framework

    I do my best to keep this short, since if it's too long we just don't run it
    """

    sim = PySimulation(
        percent_adoptions=(0.5,),
        scenario_configs=(
            ScenarioConfig(
                ScenarioCls=SubprefixHijack,
                AdoptPolicyCls=ROVSimplePolicy,
                BasePolicyCls=BGPSimplePolicy,
                num_attackers=1,
            ),
        ),
        num_trials=1,
        output_dir=tmp_path / "test_sim_inputs",
        parse_cpus=1,
    )
    sim.run()
