from typing import Optional, Union

from frozendict import frozendict
from bgpy.as_graphs import ASGraphInfo, PeerLink, CustomerProviderLink as CPLink
from bgpy.enums import SpecialPercentAdoptions, ASNs
from bgpy.simulation_engine import BaseSimulationEngine, Announcement
from bgpy.simulation_framework import Scenario, ScenarioConfig, ROAInfo, ValidPrefix
from bgpy.simulation_framework.scenarios.preprocess_anns_funcs import (
    PREPROCESS_ANNS_FUNC_TYPE,
    noop,
)
from bgpy.tests.engine_tests import EngineTestConfig


class CustomScenario(Scenario):
    """
    Allows API users to create their own scenario using self-defined announcements and
    ROAs.
    """

    def __init__(
        self,
        *,
        scenario_config: ScenarioConfig,
        percent_adoption: Union[float, SpecialPercentAdoptions] = 0,
        engine: Optional[BaseSimulationEngine] = None,
        prev_scenario: Optional["Scenario"] = None,
        preprocess_anns_func: PREPROCESS_ANNS_FUNC_TYPE = noop,
    ):
        super().__init__(
            scenario_config=scenario_config,
            percent_adoption=percent_adoption,
            engine=engine,
            prev_scenario=prev_scenario,
            preprocess_anns_func=preprocess_anns_func,
        )
        self.announcements = self._add_roa_info_to_anns(
            announcements=self.scenario_config.override_announcements,
            engine=engine,
            prev_scenario=prev_scenario,
        )
        print(self.announcements)
        print(self.roa_infos)

    def _get_attacker_asns(
        self,
        override_attacker_asns: Optional[frozenset[int]],
        engine: Optional[BaseSimulationEngine],
        prev_scenario: Optional["Scenario"],
    ) -> frozenset[int]:
        # If this method is not overriden and there are no attackers in
        # override_attacker_asns, an attacker AS is chosen at random. We instead want
        # to return an empty set, so we ensure override_attack_asns is returned as long
        # as it is defined.
        if override_attacker_asns is not None:
            return override_attacker_asns

        return super()._get_attacker_asns(override_attacker_asns, engine, prev_scenario)

    def _get_announcements(self, *args, **kwargs):
        # Announcements will be populated from the scenario config's
        # override_announcements
        if len(self.scenario_config.override_announcements) == 0:
            raise ValueError("Scenario config must specify announcements")
        return ()


r"""
    1
     \
     2 - 3
    /     \
   777     666
"""
as_graph_info = ASGraphInfo(
    peer_links=frozenset([PeerLink(2, 3)]),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=3, customer_asn=ASNs.ATTACKER.value),
        ]
    ),
)


anns = (Announcement(prefix="1.2.0.0/16", as_path=tuple([777]), seed_asn=777),)
roas = (ROAInfo(prefix="1.2.0.0/16", origin=777),)


internal_config_004 = EngineTestConfig(
    name="internal_004",
    desc="Valid prefix done with custom announcements",
    scenario_config=ScenarioConfig(
        ScenarioCls=CustomScenario,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({}),
        override_announcements=anns,
        override_roa_infos=roas,
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info,
)
