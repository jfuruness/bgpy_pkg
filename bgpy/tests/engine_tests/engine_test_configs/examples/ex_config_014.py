from frozendict import frozendict
from bgpy.enums import ASNs
from .as_graph_info_000 import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGP, BGPSec
from bgpy.simulation_framework import (
    ScenarioConfig,
    PrefixHijack,
    preprocess_anns_funcs,
)


desc = (
    "Neighbor spoofing prefix hijack with bgpsec simple\n"
    "BGPSec is security third, which doesn't amount to much\n"
    "AS 2 is saved, but as long as the chain is broken, AS 5"
    " is still hijacked"
)

ex_config_014 = EngineTestConfig(
    name="ex_014_neighbor_spoofing_hijack_bgpsec",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=PrefixHijack,
        preprocess_anns_func=preprocess_anns_funcs.neighbor_spoofing_hijack,
        BasePolicyCls=BGPSec,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                ASNs.ATTACKER.value: BGP,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)
