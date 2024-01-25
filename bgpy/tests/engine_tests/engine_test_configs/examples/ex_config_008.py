from frozendict import frozendict
from bgpy.enums import ASNs
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import (
    BGPSimplePolicy,
    BGPPolicy,
    ROVSimplePolicy,
    ROVPolicy,
)
from bgpy.simulation_framework import (
    ScenarioConfig,
    NonRoutedPrefixHijack,
)


desc = "NonRoutedPrefixhijack with ROV simple"

ex_config_008 = EngineTestConfig(
    name="ex_008_non_routed_prefix_hijack_rov_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=NonRoutedPrefixHijack,
        BasePolicyCls=BGPSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict({9: ROVSimplePolicy}),
    ),
    as_graph_info=as_graph_info_000,
)
