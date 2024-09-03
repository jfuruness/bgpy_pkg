from frozendict import frozendict

from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import BGPFull, PeerROVFull
from bgpy.simulation_framework import ScenarioConfig, SubprefixHijack
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = "Subprefix hijack with Peer ROV"

ex_config_007 = EngineTestConfig(
    name="ex_007_subprefix_hijack_peer_rov",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict({9: PeerROVFull}),
    ),
    as_graph_info=as_graph_info_000,
)
