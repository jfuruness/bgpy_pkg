from frozendict import frozendict
from bgpy.enums import ASNs
from .as_graph_info_000 import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGPPolicy, ASPAPolicy
from bgpy.simulation_framework import (
    ScenarioConfig,
    AccidentalRouteLeak,
    preprocess_anns_funcs,
)


desc = "accidental route leak against ASPA"

ex_config_022 = EngineTestConfig(
    name="ex_022_route_leak_aspa_upstream_verification",
    desc=desc,
    propagation_rounds=2,  # Required for route leaks
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        preprocess_anns_func=preprocess_anns_funcs.noop,
        BasePolicyCls=BGPPolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                1: ASPAPolicy,
                2: ASPAPolicy,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
