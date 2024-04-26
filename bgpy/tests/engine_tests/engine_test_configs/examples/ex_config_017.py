from frozendict import frozendict
from bgpy.enums import ASNs
from .as_graph_info_000 import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGP, PathEnd
from bgpy.simulation_framework import (
    ScenarioConfig,
    PrefixHijack,
    preprocess_anns_funcs,
)


desc = (
    "shortest path export all attack against pathend simple\n"
    "PathEnd checks the end of the path for valid providers\n"
    "so anything beyond the third AS is not protected"
)

ex_config_017 = EngineTestConfig(
    name="ex_017_shortest_path_export_all_pathend_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=PrefixHijack,
        preprocess_anns_func=preprocess_anns_funcs.shortest_path_export_all_hijack,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                1: PathEnd,
                ASNs.VICTIM.value: PathEnd,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
