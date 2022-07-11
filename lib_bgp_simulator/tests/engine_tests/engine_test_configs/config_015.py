from ..graphs import Graph018
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import ValidPrefix


class Config015(EngineTestConfig):
    """Contains config options to run a test"""

    name = "015"
    desc = "Test of path length preference"
    scenario = ValidPrefix(attacker_asns={ASNs.ATTACKER.value},
                           victim_asns={ASNs.VICTIM.value},
                           AdoptASCls=None,
                           BaseASCls=BGPSimpleAS)
    graph = Graph018()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
