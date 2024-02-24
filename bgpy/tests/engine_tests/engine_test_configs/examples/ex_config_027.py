from frozendict import frozendict
from bgpy.enums import ASNs
from .as_graph_info_000 import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGP, ASPA
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
    scenario_config=ScenarioConfig(
        ScenarioCls=PrefixHijack,
        preprocess_anns_func=preprocess_anns_funcs.shortest_path_export_all_hijack,
        BasePolicyCls=BGP,
        AdoptPolicyCls=ASPA,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
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
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
