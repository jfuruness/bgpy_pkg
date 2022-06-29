from ..graphs import Graph006
from ..utils import EngineTestConfig

from ....engine import BGPSimpleAS, ROVAS
from ....enums import ASNs
from ....scenarios import NonRoutedPrefixHijack


class Config012(EngineTestConfig):
    """Contains config options to run a test"""

    name = "012"
    desc = "NonRouted Prefix Hijack"
    scenario = NonRoutedPrefixHijack(attacker_asn=ASNs.ATTACKER.value,
                                     victim_asn=ASNs.VICTIM.value,
                                     AdoptASCls=ROVAS,
                                     BaseASCls=BGPSimpleAS)
    graph = Graph006()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
