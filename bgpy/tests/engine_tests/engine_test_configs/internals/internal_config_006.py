from typing import TYPE_CHECKING

from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs, Prefixes, SpecialPercentAdoptions, Timestamps
from bgpy.simulation_engine import BGPFull
from bgpy.simulation_framework import Scenario, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine

r"""Graph to test that an invalid ann can't be chosen post withdrawal
                       1
                      / \
                   666   777
"""

as_graph_info = ASGraphInfo(
    peer_links=frozenset(),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
        ]
    ),
)


class InvalidAnnPostWithdrawalScenario(Scenario):
    """Valid ann from victim that later is withdrawa, routing loop from attacker

    This is to test that the attacker's ann (with loop) will not get chosen in r2
    """

    min_propagation_rounds: int = 2

    def _get_announcements(
        self,
        *,
        engine: "BaseSimulationEngine | None" = None,
    ) -> tuple["Ann", ...]:
        """Valid ann from victim, routing loop in attacker"""

        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(victim_asn,),
                    timestamp=Timestamps.VICTIM.value,
                )
            )

        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(attacker_asn, 1),  # Hardcoded routing loop for test
                    seed_asn=attacker_asn,
                    next_hop_asn=attacker_asn,
                    timestamp=Timestamps.ATTACKER.value,
                )
            )

        return tuple(anns)

    def post_propagation_hook(
        self,
        engine: "BaseSimulationEngine",
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        propagation_round: int,
    ) -> None:
        """Useful hook for post propagation"""

        if propagation_round == 0:
            for victim_asn in self.victim_asns:
                as_obj = engine.as_graph.as_dict[victim_asn]
                withdraw_ann = as_obj.policy.local_rib.pop(Prefixes.PREFIX.value).copy(
                    {"withdraw": True}
                )
                as_obj.policy.withdraw_ann_from_neighbors(withdraw_ann)


internal_config_006 = EngineTestConfig(
    name="internal_config_006",
    desc=("Tests that withdrawals don't select invalid anns"),
    scenario_config=ScenarioConfig(
        ScenarioCls=InvalidAnnPostWithdrawalScenario,
        BasePolicyCls=BGPFull,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        propagation_rounds=2,
    ),
    as_graph_info=as_graph_info,
)
