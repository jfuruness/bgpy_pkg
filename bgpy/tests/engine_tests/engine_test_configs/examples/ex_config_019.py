from frozendict import frozendict
from bgpy.enums import ASNs
from .as_graph_info_000 import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGP, OnlyToCustomers
from bgpy.simulation_framework import (
    ScenarioConfig,
    AccidentalRouteLeak,
    preprocess_anns_funcs,
)


desc = (
    "accidental route leak against OnlyToCustomersSimple\n"
    "This policy sets the only_to_customers attribute"
    "specified in RFC 9234 \n"
    "which protects against simple route leaks"
)

ex_config_019 = EngineTestConfig(
    name="ex_019_route_leak_otc_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        preprocess_anns_func=preprocess_anns_funcs.noop,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                1: OnlyToCustomers,
                2: OnlyToCustomers,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
