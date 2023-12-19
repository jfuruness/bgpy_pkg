from frozendict import frozendict
from copy import deepcopy


from bgpy.tests.engine_tests.graphs import as_graph_info_047
from bgpy.tests.engine_tests.utils import EngineTestConfig


from bgpy.simulation_engine import BGPPolicy
from bgpy.simulation_framework import ValidPrefix, ScenarioConfig
from bgpy.enums import Prefixes


class Custom33ValidPrefix(ValidPrefix):
    """Add a better announcement in round 2 to cause withdrawal"""

    def post_propagation_hook(self, engine=None, propagation_round=0, *args, **kwargs):
        if propagation_round == 1:  # second round
            ann = deepcopy(
                engine.as_dict[2].policy._local_rib.get_ann(Prefixes.PREFIX.value)
            )
            # Add a new announcement at AS 3, which will be better than the one
            # from 2 and cause a withdrawn route by 1 to 4
            # ann.seed_asn = 3
            # ann.as_path = (3,)
            object.__setattr__(ann, "seed_asn", 3)
            object.__setattr__(ann, "as_path", (3,))
            engine.as_dict[3].policy._local_rib.add_ann(ann)
            Custom33ValidPrefix.victim_asns = frozenset({2, 3})
            self.victim_asns = frozenset({2, 3})


config_033 = EngineTestConfig(
    name="033",
    desc="Test withdrawal mechanism caused by better announcement",
    scenario_config=ScenarioConfig(
        ScenarioCls=Custom33ValidPrefix,
        BasePolicyCls=BGPPolicy,
        override_victim_asns=frozenset({2}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_047,
    propagation_rounds=3,
)
