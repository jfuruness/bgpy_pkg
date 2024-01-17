from frozendict import frozendict
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_006
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import (
    BGPSimplePolicy,
    ROVSimplePolicy,
)
from bgpy.enums import ASNs
from bgpy.simulation_framework import (
    ScenarioConfig,
    NonRoutedPrefixHijack,
)


config_011 = EngineTestConfig(
    name="011",
    desc="NonRouted Prefix Hijack",
    scenario_config=ScenarioConfig(
        ScenarioCls=NonRoutedPrefixHijack,
        AdoptPolicyCls=ROVSimplePolicy,
        BasePolicyCls=BGPSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict({2: ROVSimplePolicy}),
    ),
    as_graph_info=as_graph_info_006,
)
