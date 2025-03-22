from frozendict import frozendict

from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.shared.enums import (
    ASNs,
)
from bgpy.simulation_engine import (
    BGPiSecTransitiveOnlyToCustomers,
)
from bgpy.simulation_engine.policies.bgp.bgp.bgp import BGP
from bgpy.simulation_framework.scenarios.custom_scenarios.accidental_route_leak import (
    AccidentalRouteLeak,
)
from bgpy.simulation_framework.scenarios.scenario_config import ScenarioConfig
from bgpy.tests.engine_tests.utils.engine_test_config import EngineTestConfig

internal_config_010_bgpisec = EngineTestConfig(
    name="internal_config_010_bgpisec",
    desc="""
    In this diagram, the attacker AS (AS 666) attempts a route leak to AS 3,
    trying to capture all traffic AS 3 and AS 5 send to AS 777. The attack is
    foiled by the signed OTC_4 that AS 666 cannot remove, as it is part of the
    signed transitive signature from AS 777 to AS 4.

    When the leaked route from AS 666 is received by the BGP-iSec-speaking
    AS 3, it is dropped because it contains a signed OTC_4 and arrives via a
    customer interface. Without the signed OTC of BGP-iSec, the attacker could
    remove the OTC attribute, and AS 3 would have routed traffic to AS 777 via
    AS 666.
    """,
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        BasePolicyCls=BGPiSecTransitiveOnlyToCustomers,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        propagation_rounds=2,
        hardcoded_asn_cls_dict=frozendict({2: BGP, 5: BGP}),
    ),
    as_graph_info=ASGraphInfo(
        customer_provider_links=frozenset(
            [
                CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=4, customer_asn=3),
                CPLink(provider_asn=4, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=3, customer_asn=5),
            ]
        ),
    ),
)
