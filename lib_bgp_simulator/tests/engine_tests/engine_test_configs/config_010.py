from ..graphs import Graph003
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import SubprefixHijack


class Config010(EngineTestConfig):
    """Contains config options to run a test"""

    name = "010"
    desc = "Fig 2 (ROVSimpleAS)"
    scenario = SubprefixHijack(attacker_asns={ASNs.ATTACKER.value},
                               victim_asns={ASNs.VICTIM.value},
                               AdoptASCls=None,
                               BaseASCls=BGPSimpleAS,
                               )

    graph = Graph003()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
