from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import ASPA, BGP
from bgpy.simulation_framework import AccidentalRouteLeak, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

internal_config_015_aspa = EngineTestConfig(
    name="internal_config_015_aspa",
    desc=(
        """
    Demonstrates a case where ASPA fails to block a malicious route due to its directional enforcement.

    AS1 (attacker) leaks a prefix learned from AS2 (victim) to AS3, which runs ASPA. However, because AS1
    is AS3’s provider, ASPA does not validate the announcement, and AS3 accepts the route. 
    
    AS3 then passes the route to AS8 (BGP), which sends it to AS9. AS9 also runs ASPA and rejects the route because it receives
    it from a customer (AS8), and AS8 has not published ASPA data authorizing this path. 
    
    This scenario highlights that ASPA is only enforced on routes received from customers or peers—not from providers—allowing malicious 
    routes to bypass ASPA filtering if introduced upstream by providers.

"""
        
    ),
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,  # Still use this to simulate announcements
        override_victim_asns=frozenset({2}),
        override_attacker_asns=frozenset({1}),
        hardcoded_asn_cls_dict=frozendict({
            2: ASPA,     # Victim has ASPA
            3: ASPA,
            9: ASPA,     # Blocking ASPA logic here
        }),
    ),
    as_graph_info=ASGraphInfo(
        peer_links=frozenset({}),
        customer_provider_links=frozenset([
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=8),
            CPLink(provider_asn=9, customer_asn=8),  # Route goes through 8 → 9
        ]),
        diagram_ranks=(
            (2,),
            (1,),
            (3,),
            (8,),
            (9,),
        ),
    ),
)
