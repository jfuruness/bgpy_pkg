from frozendict import frozendict

from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import BGP, ROV
from bgpy.simulation_framework import NonRoutedSuperprefixHijack, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = "NonRoutedSuperprefixHijack with ROV simple"

ex_config_009 = EngineTestConfig(
    name="ex_009_non_routed_super_prefix_hijack_rov_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=NonRoutedSuperprefixHijack,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict({9: ROV}),
    ),
    as_graph_info=as_graph_info_000,
)
