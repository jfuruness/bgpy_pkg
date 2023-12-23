from frozendict import frozendict
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_002
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engines.py_simulation_engine import ROVSimplePolicy
from bgpy.enums import ASNs
from bgpy.simulation_frameworks.py_simulation_framework import ScenarioConfig, ValidPrefix


config_005 = EngineTestConfig(
    name="005",
    desc="Basic BGP Propagation (with ROV Simple AS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=ROVSimplePolicy,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_002,
)
