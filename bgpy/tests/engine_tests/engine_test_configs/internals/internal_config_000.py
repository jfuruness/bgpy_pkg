from copy import deepcopy

from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import Prefixes, SpecialPercentAdoptions
from bgpy.simulation_engine import BaseSimulationEngine, BGPFull
from bgpy.simulation_framework import ScenarioConfig, ValidPrefix
from bgpy.tests.engine_tests.utils import EngineTestConfig

as_graph_info = ASGraphInfo(
    peer_links=frozenset([PeerLink(1, 3), PeerLink(1, 5)]),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=1, customer_asn=4),
        ]
    ),
)


class Custom00ValidPrefix(ValidPrefix):
    """Add a better announcement in round 2 to cause withdrawal"""

    min_propagation_rounds: int = 3

    def post_propagation_hook(
        self,
        engine: "BaseSimulationEngine",
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        propagation_round: int,
    ) -> None:
        if propagation_round == 1:  # second round
            ann = deepcopy(
                engine.as_graph.as_dict[2].policy.local_rib.get(Prefixes.PREFIX.value)
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
            engine.as_graph.as_dict[3].policy.local_rib.add_ann(ann)
            Custom00ValidPrefix.victim_asns = frozenset({2, 3})
            self.victim_asns: frozenset[int] = frozenset({2, 3})


internal_config_000 = EngineTestConfig(
    name="internal_000",
    desc="Test withdrawal mechanism caused by better announcement",
    scenario_config=ScenarioConfig(
        ScenarioCls=Custom00ValidPrefix,
        BasePolicyCls=BGPFull,
        override_victim_asns=frozenset({2}),
        hardcoded_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info,
)
