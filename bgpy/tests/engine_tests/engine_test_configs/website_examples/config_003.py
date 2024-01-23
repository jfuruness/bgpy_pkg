from frozendict import frozendict
from bgpy.enums import ASNs
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_001
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import (
    BGPSimplePolicy,
    ROVSimplePolicy,
)
from bgpy.simulation_framework import (
    ScenarioConfig,
    SubprefixHijack,
)

desc = (
    "ROV Simple Policy\n"
    "ASes 9 and 3 are saved since ROV drops the invalid attacker subprefix"
)

config_003 = EngineTestConfig(
    name="003_rov_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGPSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict({9: ROVSimplePolicy}),
    ),
    as_graph_info=as_graph_info_001,
)
