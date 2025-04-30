from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import ASPA, BGP
from bgpy.simulation_framework import AccidentalRouteLeak, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

internal_config_013_aspa = EngineTestConfig(
    name="internal_config_013_aspa",
    desc=(
        "Same topology as 014, but with AS777 set as a customer of AS8. "
        "Tests if ASPA on AS8 can prevent the leaked route from reaching AS777."
    ),
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        override_victim_asns=frozenset({1}),
        override_attacker_asns=frozenset({2}),
        hardcoded_asn_cls_dict=frozendict(
            {
                2: BGP,
                8: ASPA,
                9: ASPA,
            }
        ),
    ),
    as_graph_info=ASGraphInfo(
        peer_links=frozenset({
            PeerLink(8, 9),
            PeerLink(9, 10),
            PeerLink(9, 3),
        }),
        customer_provider_links=frozenset([
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=5, customer_asn=1),
            CPLink(provider_asn=8, customer_asn=1),
            CPLink(provider_asn=8, customer_asn=2),
            CPLink(provider_asn=9, customer_asn=4),
            CPLink(provider_asn=10, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=13, customer_asn=8),
            CPLink(provider_asn=13, customer_asn=9),
            CPLink(provider_asn=13, customer_asn=10),
            CPLink(provider_asn=12, customer_asn=10),
            CPLink(provider_asn=8, customer_asn=777),  # ← AS8 is provider of AS777
        ]),
        diagram_ranks=(
            (ASNs.ATTACKER.value, ASNs.VICTIM.value),
            (1, 2, 3, 4),
            (5, 8, 9, 10),
            (13, 12),
            (777,),
        ),
    ),
)
