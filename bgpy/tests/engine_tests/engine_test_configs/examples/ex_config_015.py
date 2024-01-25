from frozendict import frozendict
from bgpy.enums import ASNs
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import (
    ROVSimplePolicy,
)
from bgpy.simulation_framework import (
    ScenarioConfig,
    PrefixHijack,
    preprocess_anns_funcs,
)


desc = (
    "Origin spoofing scapegoat prefix hijack thwarting ROV\n"
    "This attack reaches more ASes than just the origin hijack\n"
    "In this scenario AS 2 is the attacker, scapegoating 666"
)

ex_config_015 = EngineTestConfig(
    name="ex_015_origin_spoofing_scapegoat_prefix_hijack_rov_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=PrefixHijack,
        preprocess_anns_func=preprocess_anns_funcs.origin_spoofing_scapegoat_hijack,
        BasePolicyCls=ROVSimplePolicy,
        override_attacker_asns=frozenset({2}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict({}),
    ),
    as_graph_info=as_graph_info_000,
)
