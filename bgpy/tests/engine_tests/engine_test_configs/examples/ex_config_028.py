from frozendict import frozendict
from bgpy.enums import ASNs
from .as_graph_info_000 import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGP, ASPA
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
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        preprocess_anns_func=preprocess_anns_funcs.noop,
        BasePolicyCls=BGP,
        AdoptPolicyCls=ASPA,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                1: ASPA,
                2: ASPA,
                3: ASPA,
                4: ASPA,
                5: ASPA,
                8: ASPA,
                9: ASPA,
                10: ASPA,
                11: ASPA,
                12: ASPA,
                ASNs.VICTIM.value: ASPA,
                ASNs.ATTACKER.value: ASPA,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
