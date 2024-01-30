from frozendict import frozendict
from bgpy.enums import ASNs
from .as_graph_info_000 import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGPSimplePolicy, ASPASimplePolicy
from bgpy.simulation_framework import (
    ScenarioConfig,
    PrefixHijack,
    preprocess_anns_funcs,
)


desc = (
    "shortest path export all against ASPASimple from a customer\n"
    "AS 5 fails to detect the shortest path export all"
)

ex_config_025 = EngineTestConfig(
    name="ex_025_shortest_path_export_all_aspa_simple_customer",
    desc=desc,
    propagation_rounds=1,
    scenario_config=ScenarioConfig(
        ScenarioCls=PrefixHijack,
        preprocess_anns_func=preprocess_anns_funcs.shortest_path_export_all_hijack,
        BasePolicyCls=BGPSimplePolicy,
        AdoptPolicyCls=ASPASimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                2: ASPASimplePolicy,
                5: ASPASimplePolicy,
                10: ASPASimplePolicy,
                ASNs.VICTIM.value: ASPASimplePolicy,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
