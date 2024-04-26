from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink, CustomerProviderLink as CPLink
from bgpy.enums import ASNs
from bgpy.simulation_engine import BGP, ASPA
from bgpy.simulation_framework import (
    PrefixHijack,
    ScenarioConfig,
    preprocess_anns_funcs,
)
from bgpy.tests.engine_tests.utils import EngineTestConfig


r"""Graph to test ASPA RFC section 12

                    AS 666 - AS(4)
                      /         \
      (down-ramp)    /           \    (up-ramp)
                 AS(2)          AS(3)
                   /               \
                  /               AS(777)
                 /             (Origin AS)
              AS (1)
"""

as_graph_info = ASGraphInfo(
    peer_links=frozenset(
        [
            PeerLink(ASNs.ATTACKER.value, 4),
        ]
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=2, customer_asn=1),
            CPLink(provider_asn=ASNs.ATTACKER.value, customer_asn=2),
            CPLink(provider_asn=4, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
        ]
    ),
)


internal_config_004 = EngineTestConfig(
    name="internal_config_004",
    desc=(
        "ASPA RFC Section 12. "
        " Previously this diagram used to show an off by 1 bug for ASPA, so we"
        " prevent it from popping up again"
    ),
    scenario_config=ScenarioConfig(
        ScenarioCls=PrefixHijack,
        preprocess_anns_func=preprocess_anns_funcs.forged_origin_export_all_hijack,
        BasePolicyCls=BGP,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                1: ASPA,
                2: ASPA,
                3: ASPA,
                4: ASPA,
                ASNs.VICTIM.value: ASPA,
            }
        ),
    ),
    as_graph_info=as_graph_info,
)
