from bgpy.as_graphs import CustomerProviderLink as CPLink
from frozendict import frozendict
from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine.policies.bgp.bgp.bgp import BGP
from bgpy.simulation_engine.policies.bgpisec.bgpisec_transitive import BGPiSecTransitive
from bgpy.simulation_framework.scenarios.custom_scenarios.post_rov.shortest_path_prefix_hijack import (
    ShortestPathPrefixHijack,
)
from bgpy.simulation_framework.scenarios.scenario_config import ScenarioConfig
from bgpy.tests.engine_tests.utils.engine_test_config import EngineTestConfig


internal_config_008_bgpisec = EngineTestConfig(
    name="internal_config_008_bgpisec",
    desc="""
    Taken from the paper, testing BGP-iSec partial path verification, where BGPsec would fail because of non adopting AS (AS 800) would downgrade from that AS onward back to BGP thus allowing the attacker forged announcement to be accepted.
    If this scenario is using BGPSec - which from the point of view of AS 9 is just BGP because of downgrade from AS 2 - AS 9 would have picked the attacker AS (because smaller ASN number compare to legitimate AS 800 announcement).
    """,
    scenario_config=ScenarioConfig(
        ScenarioCls=ShortestPathPrefixHijack,
        BasePolicyCls=BGPiSecTransitive,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        propagation_rounds=2,
        hardcoded_asn_cls_dict=frozendict({800: BGP}),
    ),
    as_graph_info=ASGraphInfo(
        customer_provider_links=frozenset(
            [
                CPLink(provider_asn=800, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=800, customer_asn=9),
                CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=ASNs.ATTACKER.value, customer_asn=9),
            ]
        )
    ),
)
