from bgpy.as_graphs import CustomerProviderLink as CPLink
from frozendict import frozendict
from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine.policies.bgp.bgp.bgp import BGP
from bgpy.simulation_engine.policies.bgpisec.bgpisec import BGPiSec
from bgpy.simulation_engine.policies.bgpisec.bgpisec_full import BGPiSecFull
from bgpy.simulation_engine.policies.bgpisec.bgpisec_transitive import BGPiSecTransitive
from bgpy.simulation_engine.policies.bgpisec.bgpisec_transitive_only_to_customers import (
    BGPiSecTransitiveOnlyToCustomers,
)
from bgpy.simulation_engine.policies.bgpsec.bgpsec import BGPSec
from bgpy.simulation_framework.scenarios.custom_scenarios.accidental_route_leak import (
    AccidentalRouteLeak,
)
from bgpy.simulation_framework.scenarios.custom_scenarios.post_rov.forged_origin_prefix_hijack import (
    ForgedOriginPrefixHijack,
)
from bgpy.simulation_framework.scenarios.scenario_config import ScenarioConfig
from bgpy.tests.engine_tests.utils.engine_test_config import EngineTestConfig


internal_config_009_bgpisec = EngineTestConfig(
    name="internal_config_009_bgpisec",
    desc="""
    Taken from the BGP-iSec paper, testing BGP-iSec partial path verification, where BGPsec would fail because of non adopting AS (AS 4) would downgrade BGPSec to BGP from AS 4 onward back thus allowing the attacker forged announcement to be accepted.
    If this scenario is using BGPSec - which from the point of view of AS 9 neighbor AS is using BGP because of AS 4 and attacker downgrade to BGP - AS 9 would have picked the attacker AS's shorter path than the legitimate path from AS 4

   Using BGP-iSec transitive - the most lite implementation of BGP-iSec - which forwards the signature AS 777 to AS 2 to AS 4 onwards to AS 9. AS 666 could not provide a valid signature of having received the announcement directly from AS 777 hence why it is 
   dropped, thus thwarting the attack.
    """,
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        BasePolicyCls=BGPiSecTransitiveOnlyToCustomers,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        propagation_rounds=2,
        hardcoded_asn_cls_dict=frozendict(),
    ),
    as_graph_info=ASGraphInfo(
        customer_provider_links=frozenset(
            [
                CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=888, customer_asn=2),
                CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=888, customer_asn=9),
                CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=ASNs.ATTACKER.value, customer_asn=9),
            ]
        )
    ),
)
