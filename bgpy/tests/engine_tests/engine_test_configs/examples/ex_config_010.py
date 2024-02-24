from frozendict import frozendict
from bgpy.enums import ASNs
from .as_graph_info_000 import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import (
    BGP,
    ROV,
)
from bgpy.simulation_framework import (
    ScenarioConfig,
    NonRoutedSuperprefixPrefixHijack,
)


desc = "NonRoutedSuperprefix + Prefix Hijack with ROV simple"

ex_config_010 = EngineTestConfig(
    name="ex_010_non_routed_superprefix_prefix_hijack_rov_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=NonRoutedSuperprefixPrefixHijack,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict({9: ROV}),
    ),
    as_graph_info=as_graph_info_000,
)
