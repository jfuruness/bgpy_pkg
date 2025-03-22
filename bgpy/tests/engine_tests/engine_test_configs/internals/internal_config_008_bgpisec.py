from frozendict import frozendict

from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import BGPiSecTransitive
from bgpy.simulation_engine.policies.bgp.bgp.bgp import BGP
from bgpy.simulation_framework import ForgedOriginPrefixHijack
from bgpy.simulation_framework.scenarios.scenario_config import ScenarioConfig
from bgpy.tests.engine_tests.utils.engine_test_config import EngineTestConfig

internal_config_008_bgpisec = EngineTestConfig(
    name="internal_config_008_bgpisec",
    desc="""
    Taken from the BGP-iSec paper, testing BGP-iSec partial path verification,
    where BGPsec would fail because a non-adopting AS (AS 4) would downgrade
    BGPSec to BGP from AS 4 onward. This downgrade allows the attacker's forged
    announcement to be accepted.

    In this scenario, using BGPSec — which from the point of view of AS 9,
    its neighbor AS is using BGP due to AS 4 and the attacker's downgrade to
    BGP — AS 9 would choose the attacker AS's shorter path over the legitimate
    path from AS 4.

    Using BGP-iSec transitive — the lightest implementation of BGP-iSec —
    the signature from AS 777 is forwarded to AS 2 to AS 4 and onwards to AS 9.
    AS 666 could not provide a valid signature showing it received the
    announcement directly from AS 777. Hence, it is dropped, thwarting
    the attack.
    """,
    scenario_config=ScenarioConfig(
        ScenarioCls=ForgedOriginPrefixHijack,
        BasePolicyCls=BGPiSecTransitive,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        propagation_rounds=2,
        hardcoded_asn_cls_dict=frozendict({4: BGP, 2: BGP, 3: BGP}),
    ),
    as_graph_info=ASGraphInfo(
        customer_provider_links=frozenset(
            [
                CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=4, customer_asn=2),
                CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=4, customer_asn=9),
                CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=ASNs.ATTACKER.value, customer_asn=9),
            ]
        )
    ),
)
