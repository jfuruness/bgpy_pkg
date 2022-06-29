from ..graphs import Graph006
from ..utils import EngineTestConfig

from ....engine import BGPSimpleAS, ROVSimpleAS
from ....enums import ASNs
from ....scenarios import NonRoutedPrefixHijack


class Config011(EngineTestConfig):
    """Contains config options to run a test"""

    name = "011"
    desc = "NonRouted Prefix Hijack"
    scenario = NonRoutedPrefixHijack(attacker_asn=ASNs.ATTACKER.value,
                                     victim_asn=ASNs.VICTIM.value,
                                     AdoptASCls=ROVSimpleAS,
                                     BaseASCls=BGPSimpleAS)
    graph = Graph006()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
