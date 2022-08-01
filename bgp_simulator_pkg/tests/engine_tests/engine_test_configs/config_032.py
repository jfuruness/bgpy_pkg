from typing import Dict, Type

from lib_caida_collector import AS

from copy import deepcopy

from ..graphs import Graph040
from ..utils import EngineTestConfig


from ....simulation_engine import BGPAS
from ....simulation_framework import ValidPrefix
from ....enums import Prefixes


class Custom32ValidPrefix(ValidPrefix):
    """Add a better announcement in round 2 to cause withdrawal"""

    __slots__ = ()

    def post_propagation_hook(self, engine=None, propagation_round=0,
                              *args, **kwargs):
        if propagation_round == 1:  # second round
            ann = deepcopy(
                engine.as_dict[2]._local_rib.get_ann(Prefixes.PREFIX.value))
            # Add a new announcement at AS 3, which will be better than the one
            # from 2 and cause a withdrawn route by 1 to 4
            ann.seed_asn = 3
            ann.as_path = (3,)
            engine.as_dict[3]._local_rib.add_ann(ann)
            Custom32ValidPrefix.victim_asns = {2, 3}


class Config032(EngineTestConfig):
    """Test withdrawal caused by better announcement"""

    name = "032"
    desc = "Test withdrawal mechanism"
    scenario = Custom32ValidPrefix(
        victim_asns={2},
        AdoptASCls=None,
        BaseASCls=BGPAS)
    graph = Graph040()
    non_default_as_cls_dict: Dict[int, Type[AS]] = dict()
    propagation_rounds = 3
