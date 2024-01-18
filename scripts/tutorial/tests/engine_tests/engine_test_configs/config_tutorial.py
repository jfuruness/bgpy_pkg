from frozendict import frozendict

from bgpy.enums import ASNs
from bgpy.simulation_engine import BGPSimplePolicy
from bgpy.simulation_framework import ScenarioConfig, SubprefixHijack
from bgpy.tests import as_graph_infos
from bgpy.tests import EngineTestConfig


config_tutorial = EngineTestConfig(
    name="tutorial",
    desc="BGP hidden hijack (with simple Policy)",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGPSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_infos.as_graph_info_001,
)
