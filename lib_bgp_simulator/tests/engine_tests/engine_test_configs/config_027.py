from ..graphs import Graph040
from ..utils import EngineTestConfig

from ....engine import BGPSimpleAS
from ....enums import ASNs
from ....scenarios import MultiValidPrefix


class Config027(EngineTestConfig):
    """Contains config options to run a test"""

    name = "027"
    desc = "Test of customer preference"
    scenario = MultiValidPrefix(attacker_asn=ASNs.ATTACKER.value,
                           victim_asn=2, # the correct destination
                           victim_asns=[2, 3, 4],
                           AdoptASCls=None,
                           BaseASCls=BGPSimpleAS)
    graph = Graph040()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
