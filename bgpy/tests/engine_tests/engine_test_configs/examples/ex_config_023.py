from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import ASPA, BGP
from bgpy.simulation_framework import ForgedOriginPrefixHijack, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

as_graph_info_no_downstream = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
        ]
    ),
)


desc = (
    "Origin hijack against ASPASimple\n"
    "Testing that ASPA rejects from the upstream, but accepts from downstream"
)

ex_config_023 = EngineTestConfig(
    name="ex_023_origin_aspa_simple_downstream_verification",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=ForgedOriginPrefixHijack,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict(
            {
                2: ASPA,
                ASNs.VICTIM.value: ASPA,
            }
        ),
    ),
    as_graph_info=as_graph_info_no_downstream,
)
