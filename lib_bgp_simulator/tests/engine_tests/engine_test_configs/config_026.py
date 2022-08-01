from typing import Dict, Type

from lib_caida_collector import AS

from ..graphs import Graph019
from ..utils import EngineTestConfig

from ....simulation_engine import ROVAS
from ....enums import ASNs
from ....simulation_framework import ValidPrefix


class Config026(EngineTestConfig):
    """Contains config options to run a test"""

    name = "026"
    desc = "Test of tiebreak preference"
    scenario = ValidPrefix(victim_asns={ASNs.VICTIM.value},
                           AdoptASCls=None,
                           BaseASCls=ROVAS)
    graph = Graph019()
    non_default_as_cls_dict: Dict[int, Type[AS]] = dict()
    propagation_rounds = 1
