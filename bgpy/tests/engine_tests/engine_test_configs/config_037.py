from frozendict import frozendict
from bgpy.enums import ASNs
from bgpy.tests.engine_tests.graphs import graph_052
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGPSimpleAS, RealPeerROVSimpleAS
from bgpy.simulation_framework import ScenarioConfig, SubprefixHijack


desc = (
    "Valley Free (Gao Rexford) Demonstration\n"
    "AS 5, prefix, shows customer > provider\n"
    "AS 5, subprefix, shows peer > provider\n"
    "AS 7, prefix, shows shortest AS Path\n"
    "AS 4, subprefix, shows lowest ASN tiebreaker\n"
    "AS 5, subprefix, shows anns from peers only export to customers\n"
    "AS 6, subprefix, shows anns from providers only export to customers\n"
    "(All ASes show exporting to cusotmers)\n"
)
desc = ""

config_037 = EngineTestConfig(
    name="037_valley_free_ex_rov",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BaseASCls=BGPSimpleAS,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict({8: RealPeerROVSimpleAS}),
    ),
    graph=graph_052,
)
