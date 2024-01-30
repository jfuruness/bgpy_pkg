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
    "shortest path export all against ASPASimple from a provider\n"
    "AS prevents the attack, this is merely to check attack functionality"
)

ex_config_027 = EngineTestConfig(
    name="ex_027_shortest_path_export_all_aspa_simple_provider",
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
                3: ASPASimplePolicy,
                4: ASPASimplePolicy,
                5: ASPASimplePolicy,
                8: ASPASimplePolicy,
                9: ASPASimplePolicy,
                10: ASPASimplePolicy,
                11: ASPASimplePolicy,
                12: ASPASimplePolicy,
                ASNs.VICTIM.value: ASPASimplePolicy,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
