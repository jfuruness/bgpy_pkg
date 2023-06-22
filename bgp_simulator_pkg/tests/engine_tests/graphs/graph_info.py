from dataclasses import dataclass, field

from bgp_simulator_pkg.caida_collector import PeerLink, CustomerProviderLink as CPLink


@dataclass(frozen=True, slots=True)
class GraphInfo:
    """Contains information to build a graph"""

    customer_provider_links: set[CPLink] = field(default_factory=set)
    peer_links: set[PeerLink] = field(default_factory=set)

    @property
    def asns(self) -> list[int]:
        asns: list[int] = []
        for link in self.customer_provider_links | self.peer_links:
            asns.extend(link.asns)
        return list(sorted(set(asns)))
