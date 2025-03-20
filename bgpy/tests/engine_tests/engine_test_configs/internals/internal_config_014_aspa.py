from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import ASPA, BGP
from bgpy.simulation_framework import AccidentalRouteLeak, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

internal_config_014_aspa = EngineTestConfig(
    name="internal_config_014_aspa",
    desc=(
        "Tests ASPA-based route leak detection where AS2 leaks P2, "
        "impacting AS777. ASPA should prevent propagation beyond peers."
    ),
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        BasePolicyCls=ASPA,
        override_victim_asns=frozenset({1}),  # AS1 is the protected origin
        override_attacker_asns=frozenset({2}),  # AS2 improperly leaks P2
        hardcoded_asn_cls_dict=frozendict(
            {
                2: BGP,
            }
        ),
    ),
    as_graph_info=ASGraphInfo(
        peer_links=frozenset(
            {
                PeerLink(8, 9),
                PeerLink(9, 10),
                PeerLink(9, 3),
            }
        ),
        customer_provider_links=frozenset(
            [
                CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=5, customer_asn=1),
                CPLink(provider_asn=8, customer_asn=1),
                CPLink(provider_asn=8, customer_asn=2),
                CPLink(provider_asn=9, customer_asn=4),
                CPLink(provider_asn=10, customer_asn=ASNs.VICTIM.value),
                CPLink(
                    provider_asn=1000, customer_asn=8
                ),  # Replaced ASNs.REFLECTOR with 1000
                CPLink(
                    provider_asn=1000, customer_asn=9
                ),  # Replaced ASNs.REFLECTOR with 1000
                CPLink(
                    provider_asn=1000, customer_asn=10
                ),  # Replaced ASNs.REFLECTOR with 1000
                CPLink(provider_asn=12, customer_asn=10),
            ]
        ),
        diagram_ranks=(
            (ASNs.ATTACKER.value, ASNs.VICTIM.value),
            (1, 2, 3, 4),
            (5, 8, 9, 10),
            (1000, 12),  # Replaced ASNs.REFLECTOR with 1000
        ),
    ),
)
