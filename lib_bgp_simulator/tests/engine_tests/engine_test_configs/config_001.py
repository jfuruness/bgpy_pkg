from ..graphs import Graph001
from ...scenarios import SubprefixHijack
from ...engine import BGPSimpleAS


class Config001(EngineTestConfig):
    """Contains config options to run a test"""

    name = "001"
    desc = "TODO"
    scenario = SubprefixHijack(attacker_asn=ASNs.ATTACKER.value,
                               victim_asn=ASNs.VICTIM.value,
                               AdoptASCls=None)
    graph = Graph001
    non_default_as_cls_dict = dict()
    BaseASClsi = BGPSimpleAS
    propagation_rounds = 1
