from frozendict import frozendict

from bgpy.simulation_engine import BGP
from bgpy.simulation_framework import ScenarioConfig, AccidentalRouteLeak
from bgpy.tests.engine_tests.utils import EngineTestConfig
from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink

from bgpy.simulation_engine.policies.aspa.aspa import ASPA


as_graph_info = ASGraphInfo(
    peer_links=frozenset(),
    customer_provider_links=frozenset([
        CPLink(provider_asn=1, customer_asn=666),
        CPLink(provider_asn=2, customer_asn=666),
        CPLink(provider_asn=2, customer_asn=3),
    ]),
)

desc = "ASPA++ comparison to ASPA"

aspapp_001 = EngineTestConfig(
    name="aspapp_001",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        BasePolicyCls=ASPA,
        override_attacker_asns=frozenset({666}),
        override_victim_asns=frozenset({1}),
        hardcoded_asn_cls_dict=frozendict({
            2: BGP,
            666: BGP,
        }),
    ),
    as_graph_info=as_graph_info,
)


