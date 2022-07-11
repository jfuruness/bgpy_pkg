from ..graphs import Graph017
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import ValidPrefix


class Config019(EngineTestConfig):
    """Contains config options to run a test"""

    name = "019"
    desc = "Test of relationship preference"
    scenario = ValidPrefix(attacker_asn=ASNs.ATTACKER.value,
                           victim_asn=ASNs.VICTIM.value,
                           AdoptASCls=None,
                           BaseASCls=BGPSimpleAS)
    graph = Graph017()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
