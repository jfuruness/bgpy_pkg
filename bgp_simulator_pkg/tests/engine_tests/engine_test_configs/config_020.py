from typing import Dict, Type

from caida_collector_pkg import AS

from ..graphs import Graph017
from ..utils import EngineTestConfig

from ....simulation_engine import BGPAS
from ....enums import ASNs
from ....simulation_framework import ValidPrefix


class Config020(EngineTestConfig):
    """Contains config options to run a test"""

    name = "020"
    desc = "Test of relationship preference"
    scenario = ValidPrefix(
        attacker_asns={ASNs.ATTACKER.value},
        victim_asns={ASNs.VICTIM.value},
        AdoptASCls=None,
        BaseASCls=BGPAS,
    )
    graph = Graph017()
    non_default_as_cls_dict: Dict[int, Type[AS]] = dict()
    propagation_rounds = 1
