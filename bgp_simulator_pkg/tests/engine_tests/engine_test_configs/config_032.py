from typing import Dict, Type

from caida_collector_pkg import AS

from copy import deepcopy

from ..graphs import Graph040
from ..utils import EngineTestConfig


from ....simulation_engine import BGPAS
from ....simulation_framework import ValidPrefix
from ....enums import Prefixes


class Custom32ValidPrefix(ValidPrefix):
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
            Custom32ValidPrefix.victim_asns = {2, 3}


config_032 = EngineTestConfig(
    name="032",
    desc="Test withdrawal mechanism caused by better announcement",
    scenario_config=ScenarioConfig(
        ScenarioCls=Custom32ValidPrefix,
        BaseASCls=BGPAS,
        override_victim_asns={2},
    ),
    graph=Graph040(),
    propagation_rounds=3
)
