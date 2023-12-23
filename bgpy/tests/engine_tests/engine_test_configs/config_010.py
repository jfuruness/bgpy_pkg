from frozendict import frozendict
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_003
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engines.py_simulation_engine import BGPSimplePolicy
from bgpy.enums import ASNs
from bgpy.simulation_frameworks.py_simulation_framework import ScenarioConfig, SubprefixHijack


config_010 = EngineTestConfig(
    name="010",
    desc="Fig 2 (ROVSimplePolicy)",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGPSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_003,
)
