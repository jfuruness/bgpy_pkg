from frozendict import frozendict
from bgpy.enums import ASNs
from .as_graph_info_000 import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGP, PathendFull
from bgpy.simulation_framework import (
    ScenarioConfig,
    PrefixHijack,
    preprocess_anns_funcs,
)


desc = (
    "Origin prefix hijack with pathend\n"
    "Pathend checks the end of the path for valid providers\n"
    "and is thus protected against simple origin hijacks"
)

ex_config_016 = EngineTestConfig(
    name="ex_016_origin_prefix_hijack_pathend",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=PrefixHijack,
        preprocess_anns_func=preprocess_anns_funcs.origin_hijack,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                1: PathendFull,
                ASNs.VICTIM.value: PathendFull,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
