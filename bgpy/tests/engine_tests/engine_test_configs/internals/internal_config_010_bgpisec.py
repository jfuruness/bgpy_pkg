from frozendict import frozendict
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.simulation_engine.policies.bgp.bgp.bgp import BGP
from bgpy.simulation_engine.policies.bgpisec.bgpisec_transitive_only_to_customers import (
    BGPiSecTransitiveOnlyToCustomers,
)
from bgpy.simulation_framework.scenarios.custom_scenarios.accidental_route_leak import (
    AccidentalRouteLeak,
)
from bgpy.simulation_framework.scenarios.scenario_config import ScenarioConfig
from bgpy.tests.engine_tests.utils.engine_test_config import EngineTestConfig

from bgpy.shared.enums import (
    ASNs,
)

internal_config_010_bgpisec = EngineTestConfig(
    name="internal_config_010_bgpisec",
    desc="""
    In this diagram the attacker AS (AS 666) tries to do a route leak to AS 3 attempting to capture all of the traffice AS 3 and 5 sent to 777 but is foiled by the signed OTC_4 that AS 666 cannot remove because it is part of the signed transitive signature from AS 777 to AS 4.

    When AS 666 leaked route is received by the BGP-iSec speaking AS 3 it dropped the announcement because it contains a signed OTC_4 because it is comming from a customer interface. Without signed OTC of BGP-iSec the attacker could remove the OTC attribute and AS 3 would route traffic to AS 777 to AS 666.
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
