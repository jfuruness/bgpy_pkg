from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.as_graphs.base.links.peer_link import PeerLink
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine.policies.bgpisec.bgpisec_transitive_only_to_customers import (
    BGPiSecTransitiveOnlyToCustomers,
)
from bgpy.simulation_framework.scenarios.custom_scenarios.accidental_route_leak import (
    AccidentalRouteLeak,
)
from bgpy.simulation_framework.scenarios.scenario_config import ScenarioConfig
from bgpy.tests.engine_tests.utils.engine_test_config import EngineTestConfig


internal_config_009_bgpisec = EngineTestConfig(
    name="internal_config_009_bgpisec",
    desc="""
    Taken from the BGP-iSec paper,  here the attacker is intentionally route leak the AS 
    """,
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        BasePolicyCls=BGPiSecTransitiveOnlyToCustomers,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        propagation_rounds=2,
    ),
    as_graph_info=ASGraphInfo(
        peer_links=frozenset([PeerLink(2, 3)]),
        customer_provider_links=frozenset(
            [
                CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
            ]
        ),
    ),
)
