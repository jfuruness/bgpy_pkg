from ..graphs import Graph018
from ..utils import EngineTestConfig

from ....engine import ROVAS
from ....enums import ASNs
from ....scenarios import ValidPrefix


class Config018(EngineTestConfig):
    """Contains config options to run a test"""

    name = "018"
    desc = "Test of path length preference"
    scenario = ValidPrefix(attacker_asn=ASNs.ATTACKER.value,
                           victim_asn=ASNs.VICTIM.value,
                           AdoptASCls=None,
                           BaseASCls=ROVAS)
    graph = Graph018()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
