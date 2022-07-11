from ..graphs import Graph018
from ..utils import EngineTestConfig

from ....simulation_engine import ROVSimpleAS
from ....enums import ASNs
from ....simulation_framework import ValidPrefix


class Config017(EngineTestConfig):
    """Contains config options to run a test"""

    name = "017"
    desc = "Test of path length preference"
    scenario = ValidPrefix(attacker_asn=ASNs.ATTACKER.value,
                           victim_asn=ASNs.VICTIM.value,
                           AdoptASCls=None,
                           BaseASCls=ROVSimpleAS)
    graph = Graph018()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
