from typing import Optional, Union

from frozendict import frozendict
from bgpy.as_graphs import ASGraphInfo, PeerLink, CustomerProviderLink as CPLink
from bgpy.enums import SpecialPercentAdoptions, ASNs
from bgpy.simulation_engine import BaseSimulationEngine, Announcement, ROV
from bgpy.simulation_framework import Scenario, ScenarioConfig, ROAInfo
from bgpy.simulation_framework.scenarios.preprocess_anns_funcs import (
    PREPROCESS_ANNS_FUNC_TYPE,
    noop,
)
from bgpy.tests.engine_tests import EngineTestConfig


class CustomScenario(Scenario):
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
        # Merge ROA with announcements
        self.announcements = self._add_roa_info_to_anns(
            announcements=self.scenario_config.override_announcements,
            engine=engine,
            prev_scenario=prev_scenario,
        )

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


anns = (
    Announcement(prefix="1.2.0.0/16", as_path=tuple([777]), seed_asn=777),
    Announcement(prefix="1.2.0.0/24", as_path=tuple([666]), seed_asn=666),
)
roas = (ROAInfo(prefix="1.2.0.0/16", origin=777),)


internal_config_005 = EngineTestConfig(
    name="internal_005",
    desc="Subprefix hijack done with custom announcements and ROAs",
    scenario_config=ScenarioConfig(
        ScenarioCls=CustomScenario,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_announcements=anns,
        override_roa_infos=roas,
        override_non_default_asn_cls_dict=frozendict({3: ROV}),
    ),
    as_graph_info=as_graph_info,
)
