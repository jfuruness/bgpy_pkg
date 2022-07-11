from ..graphs import Graph040
from ..utils import EngineTestConfig

from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import MultiValidPrefix


class Config028(EngineTestConfig):
    """Contains config options to run a test"""

    name = "028"
    desc = "Test of peer preference"
    scenario = MultiValidPrefix(attacker_asn=ASNs.ATTACKER.value,
                                victim_asn=3,  # the correct destination
                                victim_asns=[2, 3],
                                AdoptASCls=None,
                                BaseASCls=BGPSimpleAS)
    graph = Graph040()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
