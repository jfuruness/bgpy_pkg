from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs, Prefixes
from bgpy.simulation_engine import ASPA, BGP
from bgpy.simulation_framework import AccidentalRouteLeak, ScenarioConfig    
from bgpy.tests.engine_tests.utils import EngineTestConfig

r"""
Modified ASPA Route Leak Attack Topology

                      AS 1 (Tier 1)            AS 2 (Tier 1)
                     /       \                 /       \
                   AS 3      AS 4           AS 7       AS 8
                  /   \      /   \          /   \      /   \
                AS 5   AS 6  AS 9  AS 10  AS 11  AS 13   AS 14
                 |       |          |         |    
                 |       |          |         |
              (ASPA)    (BGP)      (BGP)    (ASPA)
                 \       /
                 Attacker (AS 12)
"""

# Define AS Graph with proper attack topology
as_graph_info = ASGraphInfo(
    peer_links=frozenset({
        PeerLink(1, 2),
        PeerLink(3, 4),
        PeerLink(7, 8),
        PeerLink(9, 10),
    }),
    customer_provider_links=frozenset({
        CPLink(provider_asn=1, customer_asn=3),
        CPLink(provider_asn=1, customer_asn=4),
        CPLink(provider_asn=2, customer_asn=7),
        CPLink(provider_asn=2, customer_asn=8),
        CPLink(provider_asn=3, customer_asn=5),
        CPLink(provider_asn=3, customer_asn=6),
        CPLink(provider_asn=4, customer_asn=9),
        CPLink(provider_asn=4, customer_asn=10),
        CPLink(provider_asn=7, customer_asn=11),
        CPLink(provider_asn=8, customer_asn=13),
        CPLink(provider_asn=9, customer_asn=12), 
        CPLink(provider_asn=10, customer_asn=12),
        CPLink(provider_asn=11, customer_asn=12),
    }),
)

internal_config_008_aspa = EngineTestConfig(
    name="internal_config_008_aspa",
    desc=(
        "Tests ASPA validation against an expanded route leak attack scenario. "
        "Ensures ASPA protects most ASes but allows one BGP AS to be infected."
    ),
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        BasePolicyCls=BGP,
        override_victim_asns=frozenset({6}),
        override_attacker_asns=frozenset({12}),
        hardcoded_asn_cls_dict=frozendict({
            1: ASPA,
            2: ASPA,
            3: ASPA,
            4: ASPA,
            5: ASPA,  
            6: BGP,   
            7: ASPA,
            8: ASPA,
            9: BGP,  
            10: ASPA,
            11: BGP,  
            12: BGP, 
            13: ASPA, 
            14: ASPA,
        }),
    ),
    as_graph_info=as_graph_info,
)
