from frozendict import frozendict
from copy import deepcopy

from bgpy.tests.engine_tests.graphs import graph_040
from bgpy.tests.engine_tests.utils import EngineTestConfig


from bgpy.simulation_engine import BGPAS
from bgpy.simulation_framework import ValidPrefix, ScenarioConfig
from bgpy.enums import Prefixes


class Custom34ValidPrefix(ValidPrefix):
    """Add a better announcement in round 2 to cause withdrawal"""

    def post_propagation_hook(self, engine=None, propagation_round=0, *args, **kwargs):
        if propagation_round == 1:  # second round
            ann = deepcopy(engine.as_dict[2]._local_rib.get_ann(Prefixes.PREFIX.value))
            # Add a new announcement at AS 3, which will be better than the one
            # from 2 and cause a withdrawn route by 1 to 4
            # ann.seed_asn = 3
            # ann.as_path = (3,)
            object.__setattr__(ann, "seed_asn", 3)
            object.__setattr__(ann, "as_path", (3,))
            engine.as_dict[3]._local_rib.add_ann(ann)
            Custom34ValidPrefix.victim_asns = frozenset({2, 3})

        if propagation_round == 2:  # third round
            ann = deepcopy(engine.as_dict[3]._local_rib.get_ann(Prefixes.PREFIX.value))
            object.__setattr__(ann, "withdraw", True)
            # ann.withdraw = True
            # Remove the original announcement from 3
            # The one from 2 is now the next-best
            engine.as_dict[3]._local_rib.remove_ann(Prefixes.PREFIX.value)
            engine.as_dict[3]._ribs_out.remove_entry(1, Prefixes.PREFIX.value)
            engine.as_dict[3]._send_q.add_ann(1, ann)
            Custom34ValidPrefix.victim_asns = frozenset({2})


config_034 = EngineTestConfig(
    name="034",
    desc="Test withdrawal mechanism choosing next best announcement",
    scenario_config=ScenarioConfig(
        ScenarioCls=Custom34ValidPrefix,
        BaseASCls=BGPAS,
        override_victim_asns=frozenset({2}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    graph=graph_040,
    propagation_rounds=4,
)
