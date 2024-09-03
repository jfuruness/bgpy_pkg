from frozendict import frozendict

from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import BGPFull
from bgpy.simulation_framework import ScenarioConfig, SubprefixHijack
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = "Subprefix hijack with BGP"

ex_config_003 = EngineTestConfig(
    name="ex_003_subprefix_hijack_bgp",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_000,
)
