from frozendict import frozendict

from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.shared.enums import (
    ASNs,
)
from bgpy.simulation_engine import (
    BGPiSecTransitiveProConID,
)
from bgpy.simulation_engine.policies.bgp.bgp.bgp import BGP
from bgpy.simulation_framework import (
    ShortestPathPrefixHijack,
)
from bgpy.simulation_framework.scenarios.scenario_config import ScenarioConfig
from bgpy.tests.engine_tests.utils.engine_test_config import EngineTestConfig

internal_config_011_bgpisec = EngineTestConfig(
    name="internal_config_011_bgpisec",
    desc="""
    Taken from the paper, the attacker (AS 666) is targeting AS 5 by leaking
    the announcement it received from AS 4. However, AS 3 detects this leak
    and drops the message.

    AS 3 considers the announcement coming from AS 666 to its customer
    interface to be invalid. It applies rule (ii) of ProConID-valid checking
    and sees that AS 3 is not listed in the ProConID-list of AS 777.

    Because the path AS 666 announced contains AS 1, if this were a
    valley-free announcement, AS 3 would have been in the ProConID-list of
    AS 777, since AS 3 is a ProConID-adopting provider of AS 777.
    """,
    scenario_config=ScenarioConfig(
        ScenarioCls=ShortestPathPrefixHijack,
        BasePolicyCls=BGPiSecTransitiveProConID,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        propagation_rounds=2,
        hardcoded_asn_cls_dict=frozendict({2: BGP, 5: BGP}),
    ),
    requires_provider_cones=True,
    as_graph_info=ASGraphInfo(
        customer_provider_links=frozenset(
            [
                CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=4, customer_asn=2),
                CPLink(provider_asn=4, customer_asn=3),
                CPLink(provider_asn=4, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=3, customer_asn=5),
            ]
        ),
    ),
)
