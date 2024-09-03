from frozendict import frozendict

from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import ROV
from bgpy.simulation_framework import ForgedOriginPrefixHijack, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = (
    "Origin prefix hijack thwarting ROV\n"
    "This also demonstrates the loop prevention mechanism at 777"
)

ex_config_012 = EngineTestConfig(
    name="ex_012_forged_origin_export_all_hijack_rov_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=ForgedOriginPrefixHijack,
        BasePolicyCls=ROV,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict({}),
    ),
    as_graph_info=as_graph_info_000,
)
