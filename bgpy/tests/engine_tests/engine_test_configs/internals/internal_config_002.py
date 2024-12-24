from functools import cached_property
from typing import TYPE_CHECKING

from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs, Prefixes, SpecialPercentAdoptions
from bgpy.simulation_engine import (
    BGPFullIgnoreInvalid,
    BGPFullSuppressWithdrawals,
    RoSTFull,
)
from bgpy.simulation_framework import ScenarioConfig, ValidPrefix
from bgpy.tests.engine_tests.utils import EngineTestConfig

if TYPE_CHECKING:
    from bgpy.simulation_engine import BaseSimulationEngine

as_graph_info = ASGraphInfo(
    peer_links=frozenset(),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=2, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=ASNs.ATTACKER.value, customer_asn=4),
            CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
        ]
    ),
)


class WithdrawalValidPrefixScenario(ValidPrefix):
    """Valid ann from victim that later is withdrawa, routing loop from attacker

    This is to test that the attacker's ann (with loop) will not get chosen in r2
    """

    min_propagation_rounds: int = 2

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

    @cached_property
    def _default_adopters(self) -> frozenset[int]:
        """We don't want the victim to adopt here"""

        return frozenset()


internal_config_002 = EngineTestConfig(
    name="internal_config_002",
    desc=("Tests RoSTFull"),
    scenario_config=ScenarioConfig(
        ScenarioCls=WithdrawalValidPrefixScenario,
        BasePolicyCls=BGPFullIgnoreInvalid,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        propagation_rounds=2,
        hardcoded_asn_cls_dict=frozendict(
            {
                1: BGPFullIgnoreInvalid,
                2: RoSTFull,
                3: BGPFullIgnoreInvalid,
                ASNs.ATTACKER.value: BGPFullSuppressWithdrawals,
                4: RoSTFull,
                ASNs.VICTIM.value: BGPFullIgnoreInvalid,
            }
        ),
    ),
    as_graph_info=as_graph_info,
)
