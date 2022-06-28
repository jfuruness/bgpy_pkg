from ..graphs import Graph001
from ..utils import EngineTestConfig

from ....engine import BGPSimpleAS
from ....enums import ASNs
from ....scenarios import SubprefixHijack


class Config001(EngineTestConfig):
    """Contains config options to run a test"""

    name = "001"
    desc = "TODO - insert description/caption here"
    scenario = SubprefixHijack(attacker_asn=ASNs.ATTACKER.value,
                               victim_asn=ASNs.VICTIM.value,
                               AdoptASCls=None)
    graph = Graph001()
    non_default_as_cls_dict = dict()
    BaseASCls = BGPSimpleAS
    propagation_rounds = 1
