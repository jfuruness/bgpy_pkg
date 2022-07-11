from ..graphs import Graph040
from ..utils import EngineTestConfig


from ....simulation_engine import BGPSimpleAS
from ....enums import ASNs
from ....simulation_framework import MultiValidPrefix


class Custom29MultiValidPrefix(MultiValidPrefix):
    """A valid prefix engine input with multiple victims"""

    __slots__ = ()

    def _get_announcements(self):
        """Returns several valid prefix announcements"""
        vic_anns = super()._get_announcements()
        if vic_anns is None:
            return None

        for i in range(len(vic_anns)):
            if vic_anns[i].origin == 5:
                # longer path for AS 5 to test path length preference
                vic_anns[i].as_path = (vic_anns[i].origin, vic_anns[i].origin)
        return vic_anns


class Config029(EngineTestConfig):
    """Contains config options to run a test"""

    name = "029"
    desc = "Test of path length preference"
    scenario = Custom29MultiValidPrefix(
        attacker_asn=ASNs.ATTACKER.value,
        victim_asn=3,  # the correct destination
        victim_asns=[3, 5],
        AdoptASCls=None,
        BaseASCls=BGPSimpleAS)
    graph = Graph040()
    non_default_as_cls_dict = dict()
    propagation_rounds = 1
