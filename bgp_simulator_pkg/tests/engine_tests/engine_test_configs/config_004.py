from ..graphs import graph_002
from ..utils import EngineTestConfig

from ....simulation_engine import BGPAS
from ....enums import ASNs
from ....simulation_framework import ScenarioConfig, ValidPrefix


config_004 = EngineTestConfig(
    name="004",
    desc="Basic BGP Propagation (with full BGP AS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=BGPAS,
        override_victim_asns={ASNs.VICTIM.value},
        override_non_default_asn_cls_dict=dict(),
    ),
    graph=graph_002,
)
