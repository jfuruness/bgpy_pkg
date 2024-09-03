from frozendict import frozendict

from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import BGP, ROVPPV1Lite
from bgpy.simulation_framework import ScenarioConfig, SubprefixHijack
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = "Subprefix Hijack against ROV++V1"

ex_config_030 = EngineTestConfig(
    name="ex_030_subprefix_hijack_against_rovpp",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict(
            {
                8: ROVPPV1Lite,
                9: ROVPPV1Lite,
                ASNs.VICTIM.value: ROVPPV1Lite,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
