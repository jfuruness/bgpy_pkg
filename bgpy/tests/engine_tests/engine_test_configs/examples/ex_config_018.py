from frozendict import frozendict

from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import BGP, PathEnd
from bgpy.simulation_framework import AccidentalRouteLeak, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

from .as_graph_info_000 import as_graph_info_000

desc = (
    "accidental route leak against pathend simple\n"
    "PathEnd checks the end of the path for valid providers\n"
    "so anything beyond the third AS is not protected"
)

ex_config_018 = EngineTestConfig(
    name="ex_018_route_leak_pathend_simple",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=AccidentalRouteLeak,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict(
            {
                1: PathEnd,
                ASNs.VICTIM.value: PathEnd,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
