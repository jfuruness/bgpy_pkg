from ..graphs import Graph006
from ..utils import EngineTestConfig

from ....engine import BGPSimpleAS, ROVSimpleAS
from ....enums import ASNs
from ....scenarios import NonRoutedSuperprefixHijack


class Config013(EngineTestConfig):
    """Contains config options to run a test"""

    name = "013"
    desc = "NonRouted Superprefix Hijack"
    scenario = NonRoutedSuperprefixHijack(attacker_asn=ASNs.ATTACKER.value,
                                          victim_asn=ASNs.VICTIM.value,
                                          AdoptASCls=ROVSimpleAS,
                                          BaseASCls=BGPSimpleAS)
    graph = Graph006()
    non_default_as_cls_dict = {
        2: ROVSimpleAS
    }
    propagation_rounds = 1
