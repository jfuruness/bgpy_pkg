from ..graphs import Graph003
from ..utils import EngineTestConfig

from ....simulation_engine import ROVSimpleAS
from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import SubprefixHijack


class Config007(EngineTestConfig):
    """Contains config options to run a test"""

    name = "007"
    desc = "Fig 2 (ROVSimpleAS)"
    scenario = SubprefixHijack(attacker_asn=ASNs.ATTACKER.value,
                               victim_asn=ASNs.VICTIM.value,
                               AdoptASCls=ROVSimpleAS,
                               BaseASCls=BGPSimpleAS,
                               )

    graph = Graph003()
    non_default_as_cls_dict = {3: ROVSimpleAS,
                               4: ROVSimpleAS}
    propagation_rounds = 1
