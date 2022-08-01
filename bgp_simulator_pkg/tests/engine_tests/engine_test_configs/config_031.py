from typing import Dict, Type

from lib_caida_collector import AS

from ..graphs import Graph040
from ..utils import EngineTestConfig


from ....simulation_engine import BGPSimpleAS
from ....simulation_framework import ValidPrefix


class Custom31ValidPrefix(ValidPrefix):
    """A valid prefix engine input"""

    __slots__ = ()

    def _get_announcements(self):
        vic_ann = super()._get_announcements()[0]
        # Add 1 to the path so AS 1 rejects this
        vic_ann.as_path = (vic_ann.origin, 1, vic_ann.origin)
        return (vic_ann,)


class Config031(EngineTestConfig):
    """Contains config options to run a test"""

    name = "031"
    desc = "Test loop prevention mechanism"
    scenario = Custom31ValidPrefix(victim_asns={4},
                                   AdoptASCls=None,
                                   BaseASCls=BGPSimpleAS)
    graph = Graph040()
    non_default_as_cls_dict: Dict[int, Type[AS]] = dict()
    propagation_rounds = 1
