from typing import TYPE_CHECKING

from frozendict import frozendict
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.simulation_engine.policies.bgp.bgp.bgp import BGP
from bgpy.simulation_engine.policies.bgpisec.bgpisec_transitive_only_to_customers import (
    BGPiSecTransitiveOnlyToCustomers,
)
from bgpy.simulation_engine.policies.bgpisec.bgpisec_transitive_pro_con_id import (
    BGPiSecTransitiveProConID,
)
from bgpy.simulation_framework.scenarios.custom_scenarios.accidental_route_leak import (
    AccidentalRouteLeak,
)
from bgpy.simulation_framework.scenarios.scenario_config import ScenarioConfig
from bgpy.tests.engine_tests.utils.engine_test_config import EngineTestConfig

from bgpy.shared.enums import (
    ASNs,
)

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


internal_config_011_bgpisec = EngineTestConfig(
    name="internal_config_011_bgpisec",
    desc="""
    """,
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        # BasePolicyCls=BGPiSecTransitiveOnlyToCustomers,
        BasePolicyCls=BGPiSecTransitiveProConID,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        propagation_rounds=2,
        hardcoded_asn_cls_dict=frozendict({2: BGP}),
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
