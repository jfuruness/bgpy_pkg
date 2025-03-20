from frozendict import frozendict
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.simulation_engine.policies.bgp.bgp.bgp import BGP
from bgpy.simulation_engine.policies.bgpisec.bgpisec_transitive_pro_con_id import (
    BGPiSecTransitiveProConID,
)
from bgpy.simulation_framework.scenarios.custom_scenarios.post_rov.shortest_path_prefix_hijack import (
    ShortestPathPrefixHijack,
)
from bgpy.simulation_framework.scenarios.scenario_config import ScenarioConfig
from bgpy.tests.engine_tests.utils.engine_test_config import EngineTestConfig

from bgpy.shared.enums import (
    ASNs,
)

internal_config_011_bgpisec = EngineTestConfig(
    name="internal_config_011_bgpisec",
    desc="""
    Taken from the paper, the attacker (AS 666) is trying to target AS 5 as a victim by leaking the announcement it received from AS 4, but AS 3 detected this leak and dropped the message.

    AS 3 consider the announcement comming from AS 666 to its customer interface to be invalid because it applies rule (ii) of ProConID-valid checking and sees that AS 3 is not listed in the ProConID-list of AS 777.
    Because the path that AS 666 announced cotains AS 1, if this is a valley-free announcement AS 3 would have been in the ProConID-list of AS 777 because AS 3 is a ProConID adopting provider of AS 777.
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
