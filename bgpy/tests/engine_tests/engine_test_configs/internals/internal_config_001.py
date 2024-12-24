from typing import TYPE_CHECKING

from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs, Prefixes, SpecialPercentAdoptions, Timestamps
from bgpy.simulation_engine import BaseSimulationEngine, BGPFull
from bgpy.simulation_framework import Scenario, ScenarioConfig
from bgpy.tests.engine_tests.utils import EngineTestConfig

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann

as_graph_info = ASGraphInfo(
    peer_links=frozenset(),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=ASNs.VICTIM.value, customer_asn=2),
            CPLink(provider_asn=2, customer_asn=3),
            CPLink(provider_asn=ASNs.ATTACKER.value, customer_asn=1),
            CPLink(provider_asn=1, customer_asn=2),
        ]
    ),
)


class WithdrawalToPopulatedRIBsInThenBetterAnnScenario(Scenario):
    """Tests that best RIBs anns are chosen post withdrawal, and tests forwarding

    Attacker announces longer path than victim. Post withdrawal, AS 2 should use
    attackers path, as should AS 3.

    Afterwards in round 3, victim announces a better path, and attacks ann should
    be withdrawn
    """

    min_propagation_rounds: int = 3

    def _get_announcements(
        self,
        *,
        engine: "BaseSimulationEngine | None" = None,
    ) -> tuple["Ann", ...]:
        """Attacker announces longer path than victim"""

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
                    as_path=(attacker_asn,),
                    seed_asn=attacker_asn,
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
        elif propagation_round == 1:
            for victim_asn in self.victim_asns:
                as_obj = engine.as_graph.as_dict[victim_asn]
                as_obj.policy.seed_ann(
                    self.scenario_config.AnnCls(
                        prefix=Prefixes.PREFIX.value,
                        as_path=(victim_asn,),
                        timestamp=Timestamps.VICTIM.value,
                    )
                )


internal_config_001 = EngineTestConfig(
    name="internal_001",
    desc="Tests that a better ann triggers a withdrawal",
    scenario_config=ScenarioConfig(
        ScenarioCls=WithdrawalToPopulatedRIBsInThenBetterAnnScenario,
        BasePolicyCls=BGPFull,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        hardcoded_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info,
)
