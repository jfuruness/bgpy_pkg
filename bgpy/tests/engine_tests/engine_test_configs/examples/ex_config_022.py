from frozendict import frozendict

from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import ASPAFull, BGPFull
from bgpy.simulation_framework import AccidentalRouteLeak, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = "accidental route leak against ASPA"

ex_config_022 = EngineTestConfig(
    name="ex_022_route_leak_aspa_upstream_verification",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict(
            {
                1: ASPAFull,
                2: ASPAFull,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
