from frozendict import frozendict
from copy import deepcopy

from bgpy.tests.engine_tests.utils import EngineTestConfig


from bgpy.simulation_engine import BGPFull
from bgpy.simulation_framework import (
    ValidPrefix,
    ScenarioConfig,
)
from bgpy.enums import Prefixes

from bgpy.as_graphs import PeerLink, CustomerProviderLink as CPLink
from bgpy.as_graphs import ASGraphInfo


r"""Graph to test relationship preference

      2
     /
5 - 1 - 3
     \
      4
"""

as_graph_info = ASGraphInfo(
    peer_links=frozenset([PeerLink(1, 3), PeerLink(1, 5)]),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=1, customer_asn=4),
        ]
    ),
)


class Custom02ValidPrefix(ValidPrefix):
    """Add a better announcement in round 2 to cause withdrawal"""

    min_propagation_rounds: int = 4

    def post_propagation_hook(self, engine=None, propagation_round=0, *args, **kwargs):
        if propagation_round == 1:  # second round
            ann = deepcopy(
                engine.as_graph.as_dict[2].policy._local_rib.get(Prefixes.PREFIX.value)
            )
            # Add a new announcement at AS 3, which will be better than the one
            # from 2 and cause a withdrawn route by 1 to 4
            # ann.seed_asn = 3
            # ann.as_path = (3,)
            object.__setattr__(ann, "seed_asn", 3)
            object.__setattr__(
                ann,
                "as_path",
                (3,),
            )
            engine.as_graph.as_dict[3].policy._local_rib.add_ann(ann)
            Custom02ValidPrefix.victim_asns = frozenset({2, 3})

        if propagation_round == 2:  # third round
            ann = deepcopy(
                engine.as_graph.as_dict[3].policy._local_rib.get(Prefixes.PREFIX.value)
            )
            object.__setattr__(ann, "withdraw", True)
            # ann.withdraw = True
            # Remove the original announcement from 3
            # The one from 2 is now the next-best
            engine.as_graph.as_dict[3].policy._local_rib.pop(
                Prefixes.PREFIX.value, None
            )
            engine.as_graph.as_dict[3].policy._ribs_out.remove_entry(
                1, Prefixes.PREFIX.value
            )
            engine.as_graph.as_dict[3].policy._send_q.add_ann(1, ann)
            Custom02ValidPrefix.victim_asns = frozenset({2})


internal_config_002 = EngineTestConfig(
    name="internal_002",
    desc="Test withdrawal mechanism choosing next best announcement",
    scenario_config=ScenarioConfig(
        ScenarioCls=Custom02ValidPrefix,
        BasePolicyCls=BGPFull,
        override_victim_asns=frozenset({2}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info,
)
