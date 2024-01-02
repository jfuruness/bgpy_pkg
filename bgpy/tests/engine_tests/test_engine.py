from dataclasses import replace
from pathlib import Path

import pytest

from bgpy.simulation_engines.cpp_simulation_engine import (
    CPPSimulationEngine,
    CPPAnnouncement,
)
from bgpy.simulation_engines.py_simulation_engine.policies import BGPPolicy, ROVPolicy
from bgpy.simulation_frameworks.cpp_simulation_framework import CPPASGraphAnalyzer

from .engine_test_configs import engine_test_configs
from .utils import EngineTester
from .utils import EngineTestConfig


cpp_configs = []
for engine_test_config in engine_test_configs:
    try:
        # These configs do bad things to announcements
        # C++ doesn't allow this
        cpp_valid = int(engine_test_config.name) not in list(range(29, 34 + 1))
        scenario_conf = engine_test_config.scenario_config
        policies = list(scenario_conf.override_non_default_asn_cls_dict.values())
        # These policies aren't supported yet
        unsupported_policies = (BGPPolicy, ROVPolicy)
        cpp_valid = cpp_valid and not any(x in policies for x in unsupported_policies)
        cpp_valid = cpp_valid and not any(
            x == scenario_conf.BasePolicyCls for x in unsupported_policies
        )
    except ValueError:
        cpp_valid = True

    if cpp_valid:
        cpp_configs.append(
            replace(
                engine_test_config,
                name="cpp_" + engine_test_config.name,
                desc="C++ Sim of " + engine_test_config.desc,
                SimulationEngineCls=CPPSimulationEngine,
                scenario_config=replace(
                    engine_test_config.scenario_config, AnnCls=CPPAnnouncement
                ),
                ASGraphAnalyzerCls=CPPASGraphAnalyzer,
            )
        )
engine_test_configs = cpp_configs + engine_test_configs
# engine_test_configs = [engine_test_configs[2]]
# print(engine_test_configs[0].name)#= [engine_test_configs[2]]


@pytest.mark.engine
class TestEngine:
    """Performs a system test on the engine

    See README for in depth details
    """

    @pytest.mark.parametrize("conf", engine_test_configs)
    def test_engine(self, conf: EngineTestConfig, overwrite: bool):
        """Performs a system test on the engine

        See README for in depth details
        """

        EngineTester(
            base_dir=self.base_dir, conf=conf, overwrite=overwrite
        ).test_engine()

    @property
    def base_dir(self) -> Path:
        """Returns test output dir"""

        return Path(__file__).parent / "engine_test_outputs"
