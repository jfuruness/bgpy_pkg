from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs, Prefixes
from bgpy.simulation_engine import ASPA, BGP
from bgpy.simulation_framework import AccidentalRouteLeak, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

r"""
ASPA Route Leak Attack Topology - Small Version

              AS 1 (Tier 1, ASPA)
               /        \
      AS 2 (ASPA)    AS 3 (BGP)
       |         \      /
     AS 4 (ASPA)   AS 5 (BGP)
       |               |
 Victim (AS 6, ASPA)  Attacker (AS 7, BGP)

- Path where attacker wins: AS 7 → AS 5 → AS 3
- Path where victim wins: AS 6 → AS 4 → AS 2
- Shared path: AS 6 → AS 5 → ?? (ASPA validation decides who wins)
"""

# Define the ASPA Route Leak Scenario with corrected AS relationships
internal_config_013_aspa = EngineTestConfig(
    name="internal_config_013_aspa",
    desc=(
        "Tests ASPA validation in a small topology. "
        "Shows a case where ASPA protects paths, an attacker wins one path, "
        "and a shared path decides the outcome."
    ),
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        BasePolicyCls=ASPA,
        override_victim_asns=frozenset({6}),
        override_attacker_asns=frozenset({7}),
        hardcoded_asn_cls_dict=frozendict(
            {
                3: BGP,
                5: BGP,
                7: BGP,  # Attacker
            }
        ),
    ),
    as_graph_info=ASGraphInfo(
        peer_links=frozenset({}),
        customer_provider_links=frozenset(
            {
                CPLink(provider_asn=1, customer_asn=2),
                CPLink(provider_asn=1, customer_asn=3),
                CPLink(provider_asn=2, customer_asn=4),
                CPLink(provider_asn=3, customer_asn=5),  # Shared path
                CPLink(provider_asn=4, customer_asn=6),  # Victim path
                CPLink(provider_asn=5, customer_asn=7),  # Attacker path
            }
        ),
    ),
)
