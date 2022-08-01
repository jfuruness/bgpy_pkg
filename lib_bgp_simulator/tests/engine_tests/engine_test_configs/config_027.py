from typing import Dict, Type

from lib_caida_collector import AS

from ..graphs import Graph040
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....simulation_framework import ValidPrefix


class Config027(EngineTestConfig):
    """Contains config options to run a test"""

    name = "027"
    desc = "Test of customer preference"
    scenario = ValidPrefix(victim_asns={2, 3, 4},
                           num_victims=3,
                           AdoptASCls=None,
                           BaseASCls=BGPSimpleAS)
    graph = Graph040()
    non_default_as_cls_dict: Dict[int, Type[AS]] = dict()
    propagation_rounds = 1
