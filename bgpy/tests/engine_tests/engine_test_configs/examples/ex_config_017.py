from frozendict import frozendict
from bgpy.enums import ASNs
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGPSimplePolicy, PathendSimplePolicy
from bgpy.simulation_framework import (
    ScenarioConfig,
    PrefixHijack,
    preprocess_anns_funcs,
)


desc = (
    "Origin prefix hijack with pathend simple\n"
    "Pathend checks the end of the path for valid providers\n"
    "and is thus protected against simple origin hijacks"
)

ex_config_017 = EngineTestConfig(
    name="ex_017_origin_prefix_hijack_pathend_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=PrefixHijack,
        preprocess_anns_func=preprocess_anns_funcs.origin_hijack,
        BasePolicyCls=BGPSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                1: PathendSimplePolicy,
                ASNs.VICTIM.value: PathendSimplePolicy,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
