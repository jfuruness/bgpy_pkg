from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.as_graphs.base.links.peer_link import PeerLink
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import (
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
    Taken from the BGP-iSec paper. Here, the attacker AS 666 is intentionally
    leaking the route it is receiving from AS 2. AS 3 receives an announcement
    to its customer interface from AS 666 with a signed OTC that AS 666 cannot
    remove, indicating a route leak. AS 3 then drops the announcement from
    AS 666 and uses the announcement from AS 2.

    If we were using BGPSec in this scenario, AS 3 would have accepted the
    leaked route from AS 666 because AS 666 is a customer of AS 3.
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
