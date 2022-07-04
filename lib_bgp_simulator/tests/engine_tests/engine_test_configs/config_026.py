from ..graphs import Graph019
from ..utils import EngineTestConfig

from ....engine import ROVAS
from ....enums import ASNs
from ....scenarios import ValidPrefix


class Config026(EngineTestConfig):
    """Contains config options to run a test"""

    name = "026"
    desc = "Test of tiebreak preference"
    scenario = ValidPrefix(attacker_asn=ASNs.ATTACKER.value,
                           victim_asn=ASNs.VICTIM.value,
                           AdoptASCls=None,
                           BaseASCls=ROVAS)
    graph = Graph019()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
