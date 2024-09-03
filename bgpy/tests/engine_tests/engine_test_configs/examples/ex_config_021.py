from frozendict import frozendict

from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import ASPA, BGP
from bgpy.simulation_framework import AccidentalRouteLeak, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = "accidental route leak against ASPASimple"

ex_config_021 = EngineTestConfig(
    name="ex_021_route_leak_aspa_simple_upstream_verification",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict(
            {
                1: ASPA,
                2: ASPA,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
