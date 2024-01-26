from frozendict import frozendict
from bgpy.enums import ASNs
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import (
    ROVSimplePolicy,
)
from bgpy.simulation_framework import (
    ScenarioConfig,
    OriginSpoofingPrefixDisconnectionHijack,
)


desc = (
    "Origin spoofing disconnection prefix hijack thwarting ROV\n"
    "This attack reaches more ASes than just the origin hijack\n"
    "Attacker also doesn't care about traffic, so they set a different next_hop"
)

ex_config_014 = EngineTestConfig(
    name="ex_014_origin_spoofing_disconnection_prefix_hijack_rov_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=OriginSpoofingPrefixDisconnectionHijack,
        BasePolicyCls=ROVSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict({}),
    ),
    as_graph_info=as_graph_info_000,
)
