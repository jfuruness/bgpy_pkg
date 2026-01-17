from ipaddress import ip_network

from frozendict import frozendict
from roa_checker import ROA

from bgpy.shared.enums import ASNs, Prefixes, Relationships, Timestamps
from bgpy.simulation_framework import Scenario, ScenarioConfig

from bgpy.simulation_engine import Announcement as Ann
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_engine import BGP

from bgpy.as_graphs import ASGraphInfo
from bgpy.as_graphs.base.links import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links import PeerLink
from bgpy.shared.enums import ASNs
from bgpy.utils import EngineRunConfig

class CustomScenario(Scenario):
    """Similar to a PrefixHijack"""

    def _get_announcements(
        self,
        *,
        engine: BaseSimulationEngine | None = None,
    ) -> tuple["Ann", ...]:

        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    next_hop_asn=victim_asn,
                    as_path=(victim_asn,),
                    timestamp=Timestamps.VICTIM.value,
                    seed_asn=victim_asn,
                    recv_relationship=Relationships.ORIGIN,
                )
            )
        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    next_hop_asn=attacker_asn,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    recv_relationship=Relationships.ORIGIN,
                )
            )
        return tuple(anns)

    def _get_roas(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: BaseSimulationEngine | None = None,
    ) -> tuple[ROA, ...]:
        """Returns a tuple of ROAs"""

        return tuple(
            [ROA(ip_network(Prefixes.PREFIX.value), x) for x in self.victim_asns]
        )

def main():
    TARGET_AS = 1
    as_graph = ASGraphInfo(
        peer_links=frozenset(
            {
                PeerLink(8, 9),
                PeerLink(9, 10),
                PeerLink(9, 3),
            }
        ),
        customer_provider_links=frozenset(
            [
                CPLink(provider_asn=1, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=2, customer_asn=ASNs.ATTACKER.value),
                CPLink(provider_asn=2, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=4, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=5, customer_asn=1),
                # CPLink(provider_asn=5, customer_asn=2),
                CPLink(provider_asn=8, customer_asn=1),
                CPLink(provider_asn=8, customer_asn=2),
                CPLink(provider_asn=9, customer_asn=4),
                CPLink(provider_asn=10, customer_asn=ASNs.VICTIM.value),
                CPLink(provider_asn=11, customer_asn=8),
                CPLink(provider_asn=11, customer_asn=9),
                CPLink(provider_asn=11, customer_asn=10),
                CPLink(provider_asn=12, customer_asn=10),
            ]
        ),
    )

    conf = EngineRunConfig(
        name="Example run",
        desc="Prefix Hijack Example",
        scenario_config=ScenarioConfig(
            ScenarioCls=CustomScenario,
            BasePolicyCls=BGP,
            override_attacker_asns=frozenset({ASNs.ATTACKER.value,})
            override_victim_asns=frozenset({ASNs.VICTIM.value,})
            hardcoded_asn_cls_dict=frozendict({
                1: ROV,
            })
        ),
        as_graph_info=as_graph
    )
    runner = EngineRunner(
        conf=conf,
        base_dir=Path.home() / "Desktop" / "example_run"
    )
    (
        engine,
        outcomes_yaml,
        graph_data_aggregator,
        scenario
    ) = runner.run_engine()
    pprint(engine.as_dict[1].local_rib)

if __name__ == "__main__":
    main()
