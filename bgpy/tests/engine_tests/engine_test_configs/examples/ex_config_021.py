from frozendict import frozendict
from bgpy.enums import ASNs
from .as_graph_info_000 import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGPSimplePolicy, ASPASimplePolicy
from bgpy.simulation_framework import (
    ScenarioConfig,
    AccidentalRouteLeak,
    preprocess_anns_funcs,
)


desc = "accidental route leak against ASPASimple"

ex_config_021 = EngineTestConfig(
    name="ex_021_route_leak_aspa_simple_upstream_verification",
    desc=desc,
    propagation_rounds=2,  # Required for route leaks
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        preprocess_anns_func=preprocess_anns_funcs.noop,
        BasePolicyCls=BGPSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                1: ASPASimplePolicy,
                2: ASPASimplePolicy,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
