from frozendict import frozendict
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_003
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import ROVSimplePolicy, BGPSimplePolicy
from bgpy.enums import ASNs
from bgpy.simulation_framework import ScenarioConfig, SubprefixHijack


config_007 = EngineTestConfig(
    name="007",
    desc="Fig 2 (ROVSimplePolicy)",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGPSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        AdoptPolicyCls=ROVSimplePolicy,
        override_non_default_asn_cls_dict=frozendict(
            {3: ROVSimplePolicy, 4: ROVSimplePolicy}
        ),
    ),
    as_graph_info=as_graph_info_003,
)
