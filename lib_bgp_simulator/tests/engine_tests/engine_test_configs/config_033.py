from copy import deepcopy

from ..graphs import Graph047
from ..utils import EngineTestConfig


from ....simulation_engine import BGPAS
from ....simulation_framework import ValidPrefix
from ....enums import ASNs, Prefixes


class Custom33ValidPrefix(ValidPrefix):
    """Add a better announcement in round 2 to cause withdrawal"""

    __slots__ = ()

    def post_propagation_hook(self, engine=None, propagation_round=0, *args, **kwargs):
        if propagation_round == 1:  # second round
            ann = deepcopy(engine.as_dict[2]._local_rib.get_ann(Prefixes.PREFIX.value))
            # Add a new announcement at AS 3, which will be better than the one
            # from 2 and cause a withdrawn route by 1 to 4
            ann.seed_asn = 3
            ann.as_path = (3,)
            engine.as_dict[3]._local_rib.add_ann(ann)
            Custom33ValidPrefix.victim_asns = {2, 3}


class Config033(EngineTestConfig):
    """Test withdrawal caused by better announcement"""

    name = "033"
    desc = "Test withdrawal mechanism"
    scenario = Custom33ValidPrefix(
        victim_asns={2},
        AdoptASCls=None,
        BaseASCls=BGPAS)
    graph = Graph047()
    non_default_as_cls_dict = dict()
    propagation_rounds = 3
