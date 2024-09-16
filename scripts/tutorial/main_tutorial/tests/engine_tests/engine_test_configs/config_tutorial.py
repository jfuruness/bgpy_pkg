from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink
from bgpy.as_graphs import CustomerProviderLink as CPLink
from bgpy.shared.enums import ASNs
from bgpy.simulation_engine import BGP
from bgpy.simulation_framework import ScenarioConfig, SubprefixHijack
from bgpy.tests import EngineTestConfig

r"""Hidden hijack example with BGP
Figure 1a in our ROV++ paper

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

config_tutorial = EngineTestConfig(
    name="tutorial",
    desc="BGP hidden hijack (with simple Policy)",
    scenario_config=ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGP,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
    ),
    as_graph_info=as_graph_info,
)
