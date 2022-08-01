from typing import Dict, Type

from lib_caida_collector import AS

from ..graphs import Graph018
from ..utils import EngineTestConfig

from ....simulation_engine import ROVAS
from ....enums import ASNs
from ....simulation_framework import ValidPrefix


class Config018(EngineTestConfig):
    """Contains config options to run a test"""

    name = "018"
    desc = "Test of path length preference"
    scenario = ValidPrefix(attacker_asns={ASNs.ATTACKER.value},
                           victim_asns={ASNs.VICTIM.value},
                           AdoptASCls=None,
                           BaseASCls=ROVAS)
    graph = Graph018()
    non_default_as_cls_dict: Dict[int, Type[AS]] = dict()
    propagation_rounds = 1
