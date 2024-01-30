from frozendict import frozendict
from bgpy.enums import ASNs
from .as_graph_info_000 import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGPSimplePolicy, ASPASimplePolicy
from bgpy.simulation_framework import (
    ScenarioConfig,
    SubprefixHijack,
    preprocess_anns_funcs,
)


desc = (
    "accidental route leak against ASPASimple\n"
    "This isn't realistic, just for testing to test the downstream"
    "Use the subprefix to check"
)

ex_config_023 = EngineTestConfig(
    name="ex_023_route_leak_aspa_simple_downstream_verification",
    desc=desc,
    propagation_rounds=2,  # Required for route leaks
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        preprocess_anns_func=preprocess_anns_funcs.origin_hijack,
        BasePolicyCls=BGPSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                2: ASPASimplePolicy,
                10: ASPASimplePolicy,
                ASNs.VICTIM.value: ASPASimplePolicy,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
