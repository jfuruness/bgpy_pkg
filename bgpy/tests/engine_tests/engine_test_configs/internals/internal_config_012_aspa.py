from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.simulation_engine import ASPA, BGP
from bgpy.simulation_framework import AccidentalRouteLeak, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

internal_config_012_aspa = EngineTestConfig(
    name="internal_config_012_aspa",
    desc=(
        "AS1 (attacker) receives prefix from its provider AS2 (victim), and leaks "
        "it to its peer AS8. AS8 propagates it to its provider AS9. ASPA at AS9 "
        "detects that AS1 is not an authorized provider, and blocks the path."
    ),
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        override_victim_asns=frozenset({2}),
        override_attacker_asns=frozenset({1}),
        hardcoded_asn_cls_dict=frozendict({
            9: ASPA,
            13: ASPA,
        }),
    ),
    as_graph_info=ASGraphInfo(
        peer_links=frozenset([
            PeerLink(1, 8),
        ]),
        customer_provider_links=frozenset([
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=8, customer_asn=3),
            CPLink(provider_asn=9, customer_asn=8),
            CPLink(provider_asn=13, customer_asn=9),
            CPLink(provider_asn=13, customer_asn=3),
        ]),
        diagram_ranks=(
            (1, 2),
            (8, 3),
            (9,),
            (13,),
        ),
    ),
)
