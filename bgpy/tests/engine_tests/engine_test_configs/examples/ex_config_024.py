from frozendict import frozendict
from bgpy.enums import ASNs
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGPFull, ASPAFull
from bgpy.simulation_framework import (
    ScenarioConfig,
    PrefixHijack,
    preprocess_anns_funcs,
)
from .ex_config_023 import as_graph_info_no_downstream


desc = (
    "Origin hijack against ASPASimple\n"
    "Testing that ASPA rejects from the upstream, but accepts from downstream"
)


ex_config_024 = EngineTestConfig(
    name="ex_024_origin_export_all_hijack_aspa_full_downstream_verification",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=PrefixHijack,
        preprocess_anns_func=preprocess_anns_funcs.forged_origin_export_all_hijack,
        BasePolicyCls=BGPFull,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict(
            {
                2: ASPAFull,
                ASNs.VICTIM.value: ASPAFull,
            }
        ),
    ),
    as_graph_info=as_graph_info_no_downstream,
)
