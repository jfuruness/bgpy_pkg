from typing import TYPE_CHECKING, Optional

from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink
from bgpy.shared.enums import ASNs, Prefixes, Relationships, Timestamps
from bgpy.simulation_engine import ASPA, BGP
from bgpy.simulation_framework import ScenarioConfig, ValidPrefix
from bgpy.tests.engine_tests.utils import EngineTestConfig

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class PrependedValidPrefix(ValidPrefix):
    """AS 1 prepends itself onto the victim's valid prefix: (1, 1, victim)"""

    def _get_announcements(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        return tuple(
            self.scenario_config.AnnCls(
                prefix=Prefixes.PREFIX.value,
                next_hop_asn=victim_asn,
                as_path=(1, 1, victim_asn),
                timestamp=Timestamps.VICTIM.value,
                seed_asn=1,
                recv_relationship=Relationships.CUSTOMERS,
            )
            for victim_asn in self.victim_asns
        )


r"""
2 is 1's provider, 3 is 1's peer, 4 is 3's customer, 5 is 4's customer

  2
  |
  1 --- 3
  |     |
 777    4
        |
        5
"""
as_graph_info = ASGraphInfo(
    peer_links=frozenset({PeerLink(1, 3)}),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=3, customer_asn=4),
            CPLink(provider_asn=4, customer_asn=5),
        ]
    ),
    diagram_ranks=((ASNs.VICTIM.value, 5), (1, 4), (2, 3)),
)

desc = (
    "ASPA must collapse prepending before verifying the AS path\n"
    "1 prepends: (1, 1, 777). 2 (from customer), 3 (from peer) and\n"
    "5 (from provider, the 1-3 peering is the only peak) must all accept it"
)

ex_config_031 = EngineTestConfig(
    name="ex_031_aspa_collapses_prepending",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=PrependedValidPrefix,
        BasePolicyCls=BGP,
        AdoptPolicyCls=ASPA,
        override_attacker_asns=frozenset(),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        hardcoded_asn_cls_dict=frozendict(
            {
                1: ASPA,
                2: ASPA,
                3: ASPA,
                5: ASPA,
            }
        ),
    ),
    as_graph_info=as_graph_info,
)
