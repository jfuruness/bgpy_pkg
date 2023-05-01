from typing import Dict, Type

from caida_collector_pkg import AS

from ..graphs import Graph006
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS, ROVAS
from ....enums import ASNs
from ....simulation_framework import NonRoutedPrefixHijack


class Config012(EngineTestConfig):
    """Contains config options to run a test"""

    name = "012"
    desc = "NonRouted Prefix Hijack"
    scenario = NonRoutedPrefixHijack(
        attacker_asns={ASNs.ATTACKER.value},
        victim_asns={ASNs.VICTIM.value},
        AdoptASCls=ROVAS,
        BaseASCls=BGPSimpleAS,
    )
    graph = Graph006()
    non_default_as_cls_dict: Dict[int, Type[AS]] = {2: ROVAS}
    propagation_rounds = 1
