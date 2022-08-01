from typing import Dict, Type

from lib_caida_collector import AS

from ..graphs import Graph002
from ..utils import EngineTestConfig

from ....simulation_engine import BGPAS
from ....enums import ASNs
from ....simulation_framework import ValidPrefix


class Config004(EngineTestConfig):
    """Contains config options to run a test"""

    name = "004"
    desc = "Basic BGP Propagation (with full BGP AS)"
    scenario = ValidPrefix(victim_asns={ASNs.VICTIM.value},
                           AdoptASCls=None,
                           BaseASCls=BGPAS)
    graph = Graph002()
    non_default_as_cls_dict: Dict[int, Type[AS]] = dict()
    propagation_rounds = 1
