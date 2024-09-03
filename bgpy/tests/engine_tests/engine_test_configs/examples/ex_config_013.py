from frozendict import frozendict

from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import ROV
from bgpy.simulation_framework import FirstASNStrippingPrefixHijack, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = (
    "Nieghbor spoofing prefix hijack thwarting ROV\n"
    "This attack reaches more ASes than just the origin hijack"
)

ex_config_013 = EngineTestConfig(
    name="ex_013_neighbor_spoofing_hijack_rov_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=FirstASNStrippingPrefixHijack,
        BasePolicyCls=ROV,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict({}),
    ),
    as_graph_info=as_graph_info_000,
)
