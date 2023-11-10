from frozendict import frozendict
from bgpy.tests.engine_tests.graphs import graph_003
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import ROVPolicy, BGPPolicy
from bgpy.enums import ASNs
from bgpy.simulation_framework import ScenarioConfig, SubprefixHijack


config_008 = EngineTestConfig(
    name="008",
    desc="Fig 2 (ROVSimplePolicy)",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        AdoptPolicyCls=ROVPolicy,
        BasePolicyCls=BGPPolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict({3: ROVPolicy, 4: ROVPolicy}),
    ),
    graph=graph_003,
)
