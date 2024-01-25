from frozendict import frozendict
from bgpy.enums import ASNs
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import (
    BGPSimplePolicy,
    BGPPolicy,
    PeerROVSimplePolicy,
    PeerROVPolicy,
)
from bgpy.simulation_framework import (
    ScenarioConfig,
    SubprefixHijack,
)


desc = "Subprefix hijack with Peer ROV Simple"

ex_config_006 = EngineTestConfig(
    name="ex_006_subprefix_hijack_peer_rov_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGPSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict({9: PeerROVSimplePolicy}),
    ),
    as_graph_info=as_graph_info_000,
)
