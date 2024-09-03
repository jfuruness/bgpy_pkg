from frozendict import frozendict

from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import BGP, PeerROV
from bgpy.simulation_framework import ScenarioConfig, SubprefixHijack
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = "Subprefix hijack with Peer ROV Simple"

ex_config_006 = EngineTestConfig(
    name="ex_006_subprefix_hijack_peer_rov_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict({9: PeerROV}),
    ),
    as_graph_info=as_graph_info_000,
)
