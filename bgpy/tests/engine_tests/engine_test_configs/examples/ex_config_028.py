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


desc = (
    "Route leak to check when v_max_complement==u_min\n"
    " (this is merely to check functionality)"
)

ex_config_028 = EngineTestConfig(
    name="ex_028_route_leak_aspa_simple_u_min_v_max_check",
    desc=desc,
    propagation_rounds=2,  # Required for route leaks
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        preprocess_anns_func=preprocess_anns_funcs.noop,
        BasePolicyCls=BGPSimplePolicy,
        AdoptPolicyCls=ASPASimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                1: ASPASimplePolicy,
                2: ASPASimplePolicy,
                3: ASPASimplePolicy,
                4: ASPASimplePolicy,
                5: ASPASimplePolicy,
                8: ASPASimplePolicy,
                9: ASPASimplePolicy,
                10: ASPASimplePolicy,
                11: ASPASimplePolicy,
                12: ASPASimplePolicy,
                ASNs.VICTIM.value: ASPASimplePolicy,
                ASNs.ATTACKER.value: ASPASimplePolicy,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
