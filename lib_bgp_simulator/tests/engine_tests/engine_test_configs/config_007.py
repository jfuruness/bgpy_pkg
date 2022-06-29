
from ..graphs import Graph003
from ..utils import EngineTestConfig

from ....engine import BGPSimpleAS
from ....enums import ASNs
from ....scenarios import SubprefixHijack


class Config007(EngineTestConfig):
    """Contains config options to run a test"""

    name = "007"
    desc = "Fig 2 (all BGPSimpleAS)"
    scenario = SubprefixHijack(attacker_asn=ASNs.ATTACKER.value,
                               victim_asn=ASNs.VICTIM.value,
                               AdoptASCls=BGPSimpleAS,
                               BaseASCls=BGPSimpleAS,
                               )

    graph = Graph003()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        # override the adopting ASNs to only be 3 and 4
        scenario._get_adopting_asns = self._get_adopting_asns

    def _get_adopting_asns(self, engine, percent_adopt):
        return [3, 4]
