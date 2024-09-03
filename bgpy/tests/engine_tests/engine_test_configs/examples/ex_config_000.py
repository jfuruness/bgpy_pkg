from frozendict import frozendict

from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import BGP
from bgpy.simulation_framework import ScenarioConfig, ValidPrefix
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = "Valid prefix with BGP Simple"

ex_config_000 = EngineTestConfig(
    name="ex_000_valid_prefix_bgp_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset(),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_000,
)
