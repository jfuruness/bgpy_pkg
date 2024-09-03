from frozendict import frozendict

from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import BGP, ROV
from bgpy.simulation_framework import ScenarioConfig, SuperprefixPrefixHijack
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = "Superprefix + Prefix Hijack with ROV simple"

ex_config_011 = EngineTestConfig(
    name="ex_011_superprefix_prefix_hijack_rov_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=SuperprefixPrefixHijack,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict({9: ROV}),
    ),
    as_graph_info=as_graph_info_000,
)
