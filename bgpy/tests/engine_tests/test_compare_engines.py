from dataclasses import replace

import pytest

from bgpy.as_graphs import CAIDAASGraphConstructor
from bgpy.simulation_engines.cpp_simulation_engine import (
    CPPSimulationEngine,
    CPPAnnouncement as CPPAnn,
)
from bgpy.simulation_engines.py_simulation_engine import (
    PySimulationEngine,
    PyAnnouncement as PyAnn,
    ROVSimplePolicy,
)
from bgpy.simulation_frameworks.py_simulation_framework import (
    ScenarioConfig,
    SubprefixHijack,
)


@pytest.mark.engine
class TestEngine:
    def test_compare_engines(self):
        """Runs multiple engines and ensures they are the same"""

        # C++ anns
        as_graph = CAIDAASGraphConstructor().run()
        cpp_sim_engine = CPPSimulationEngine(as_graph)

        scenario_config = ScenarioConfig(
            ScenarioCls=SubprefixHijack,
            AnnCls=CPPAnn,
            AdoptPolicyCls=ROVSimplePolicy,
        )
        scenario = scenario_config.ScenarioCls(
            scenario_config=scenario_config, engine=cpp_sim_engine
        )
        scenario.setup_engine(cpp_sim_engine)
        cpp_sim_engine.run(0, scenario)
        cpp_anns = cpp_sim_engine.get_announcements()
        print("done with c++")

        # Python anns
        as_graph = CAIDAASGraphConstructor().run()
        py_sim_engine = PySimulationEngine(as_graph)

        # Same scenario config just with adjustments
        scenario_config = replace(scenario_config, AnnCls=PyAnn)
        scenario = scenario_config.ScenarioCls(
            # Using prev_scenario here will ensure equality
            scenario_config=scenario_config,
            engine=py_sim_engine,
            prev_scenario=scenario,
        )
        scenario.setup_engine(py_sim_engine)
        py_sim_engine.run(0, scenario)
        py_anns = {
            as_obj.asn: list(as_obj.policy._local_rib._info.values())
            for as_obj in py_sim_engine.as_graph
        }
        print("Done with Python")

        # Compare the two
        for asn, py_list in py_anns.items():
            cpp_list = cpp_anns[asn]
            sorted_cpp_anns = list(sorted(cpp_list, key=lambda x: x.prefix))
            sorted_py_anns = list(sorted(py_list, key=lambda x: x.prefix))
            assert len(sorted_cpp_anns) == len(sorted_py_anns), "mismatch"
            for py_ann, cpp_ann in zip(sorted_py_anns, sorted_cpp_anns):
                for attr in (
                    "prefix",
                    "timestamp",
                    "as_path",  # "seed_asn",
                    "roa_valid_length",
                    "roa_origin",
                    "withdraw",
                    "traceback_end",
                ):
                    msg = f"mismatch {getattr(py_ann, attr)} {getattr(cpp_ann, attr)} for {attr}"
                    assert getattr(py_ann, attr) == getattr(cpp_ann, attr), msg
                assert py_ann.recv_relationship.value == cpp_ann.recv_relationship.value
        print("Done comparing")
