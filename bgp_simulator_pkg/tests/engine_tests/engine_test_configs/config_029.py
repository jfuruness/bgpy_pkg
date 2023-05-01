from typing import Dict, Type

from caida_collector_pkg import AS

from ..graphs import Graph040
from ..utils import EngineTestConfig


from ....simulation_engine import BGPSimpleAS
from ....simulation_framework import ValidPrefix


class Custom29MultiValidPrefix(ValidPrefix):
    """A valid prefix engine input with multiple victims"""

    __slots__ = ()

    def _get_announcements(self, *args, **kwargs):
        """Returns several valid prefix announcements"""

        vic_anns = super()._get_announcements()

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
        victim_asns={3, 5}, num_victims=2, AdoptASCls=None, BaseASCls=BGPSimpleAS
    )
    graph = Graph040()
    non_default_as_cls_dict: Dict[int, Type[AS]] = dict()
    propagation_rounds = 1
