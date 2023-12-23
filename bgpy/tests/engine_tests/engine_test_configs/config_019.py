from frozendict import frozendict
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_017
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engines.py_simulation_engine import BGPSimplePolicy
from bgpy.enums import ASNs
from bgpy.simulation_frameworks.py_simulation_framework import ScenarioConfig, ValidPrefix


config_019 = EngineTestConfig(
    name="019",
    desc="Test of relationship preference",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=BGPSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_017,
)
