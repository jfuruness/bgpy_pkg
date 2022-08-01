from typing import Dict, Type

from lib_caida_collector import AS

from ..graphs import Graph019
from ..utils import EngineTestConfig

from ....simulation_engine import ROVSimpleAS
from ....enums import ASNs
from ....simulation_framework import ValidPrefix


class Config025(EngineTestConfig):
    """Contains config options to run a test"""

    name = "025"
    desc = "Test of tiebreak preference"
    scenario = ValidPrefix(attacker_asns={ASNs.ATTACKER.value},
                           victim_asns={ASNs.VICTIM.value},
                           AdoptASCls=None,
                           BaseASCls=ROVSimpleAS)
    graph = Graph019()
    non_default_as_cls_dict: Dict[int, Type[AS]] = dict()
    propagation_rounds = 1
