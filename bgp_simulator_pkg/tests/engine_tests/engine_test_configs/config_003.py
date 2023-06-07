from typing import Dict, Type

from caida_collector_pkg import AS

from ..graphs import Graph002
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import ScenarioConfig, ValidPrefix


config_003 = EngineTestConfig(
    name="003",
    desc="Basic BGP Propagation (with simple AS)",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=BGPSimpleAS,
        override_victim_asns={ASNs.VICTIM.value},
        AdoptASCls=None,
    ),
    graph=Graph002(),
)
