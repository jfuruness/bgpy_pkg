from ..graphs import Graph019
from ..utils import EngineTestConfig

from ....simulation_engine import BGPAS
from ....enums import ASNs
from ....simulation_framework import ValidPrefix


class Config024(EngineTestConfig):
    """Contains config options to run a test"""

    name = "024"
    desc = "Test of tiebreak preference"
    scenario = ValidPrefix(attacker_asns={ASNs.ATTACKER.value},
                           victim_asns={ASNs.VICTIM.value},
                           AdoptASCls=None,
                           BaseASCls=BGPAS)
    graph = Graph019()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
