from ..graphs import Graph001
from ..utils import EngineTestConfig

from ....simulation_engine import BGPAS
from ....enums import ASNs
from ....simulation_framework import SubprefixHijack


class Config002(EngineTestConfig):
    """Contains config options to run a test"""

    name = "002"
    desc = "BGP hidden hijack"
    scenario = SubprefixHijack(attacker_asns={ASNs.ATTACKER.value},
                               victim_asns={ASNs.VICTIM.value},
                               AdoptASCls=None,
                               BaseASCls=BGPAS)
    graph = Graph001()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
