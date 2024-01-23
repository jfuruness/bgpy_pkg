from frozendict import frozendict
from bgpy.enums import ASNs
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_001
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import (
    BGPPolicy,
    ROVSimplePolicy,
)
from bgpy.simulation_framework import (
    ScenarioConfig,
    SubprefixHijack,
)

desc = (
    "BGP (with withdrawals)"
)

config_002 = EngineTestConfig(
    name="002_bgp_w_withdrawals",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGPPolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_001,
)
