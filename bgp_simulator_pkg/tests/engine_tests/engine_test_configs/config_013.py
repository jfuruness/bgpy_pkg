from typing import Dict, Type

from caida_collector_pkg import AS

from ..graphs import Graph006
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS, ROVSimpleAS
from ....enums import ASNs
from ....simulation_framework import NonRoutedSuperprefixHijack


class Config013(EngineTestConfig):
    """Contains config options to run a test"""

    name = "013"
    desc = "NonRouted Superprefix Hijack"
    scenario = NonRoutedSuperprefixHijack(attacker_asns={ASNs.ATTACKER.value},
                                          victim_asns={ASNs.VICTIM.value},
                                          AdoptASCls=ROVSimpleAS,
                                          BaseASCls=BGPSimpleAS)
    graph = Graph006()
    non_default_as_cls_dict: Dict[int, Type[AS]] = {2: ROVSimpleAS}
    propagation_rounds = 1
