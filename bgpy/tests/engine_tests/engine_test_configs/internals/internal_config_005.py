from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import ASPA, BGP, ShortestPathPrefixASPAAttacker
from bgpy.simulation_framework import ScenarioConfig, ShortestPathPrefixHijack
from bgpy.tests.engine_tests.utils import EngineTestConfig

r"""Graph to test ASPA RFC section 12

                    AS 2 - AS(4)
                      /         \
      (down-ramp)    /           \    (up-ramp)
                 AS(666)          AS(3)
                   /               \
                  /               AS(777)
                 /             (Origin AS)
              AS (1)
"""

as_graph_info = ASGraphInfo(
    peer_links=frozenset(
        [
            PeerLink(2, 4),
        ]
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=ASNs.ATTACKER.value, customer_asn=1),
            CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
            CPLink(provider_asn=4, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
        ]
    ),
)


internal_config_005 = EngineTestConfig(
    name="internal_config_005",
    desc=("Shortest path hijack, different for customers and providers"),
    scenario_config=ScenarioConfig(
        ScenarioCls=ShortestPathPrefixHijack,
        BasePolicyCls=BGP,
        AdoptPolicyCls=ASPA,
        AttackerBasePolicyCls=ShortestPathPrefixASPAAttacker,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        hardcoded_asn_cls_dict=frozendict(
            {
                1: ASPA,
                2: ASPA,
                3: ASPA,
                ASNs.VICTIM.value: ASPA,
            }
        ),
    ),
    as_graph_info=as_graph_info,
)
