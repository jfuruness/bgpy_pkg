from frozendict import frozendict
from bgpy.as_graphs import ASGraphInfo, PeerLink, CustomerProviderLink as CPLink
from bgpy.enums import ASNs
from bgpy.simulation_engine import Announcement
from bgpy.simulation_framework import ScenarioConfig, SubprefixHijack
from bgpy.tests.engine_tests import EngineTestConfig


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


internal_config_004 = EngineTestConfig(
    name="internal_004",
    desc="Valid prefix done with custom announcements",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        num_attackers=0,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({}),
        override_announcements=anns,
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info,
)
