from dataclasses import dataclass, field
from typing import Optional

from .links import PeerLink, CustomerProviderLink as CPLink


@dataclass(frozen=True, slots=True)
class ASGraphInfo:
    """Contains information to build a graph"""

    # Links
    customer_provider_links: frozenset[CPLink] = field(default_factory=frozenset)
    peer_links: frozenset[PeerLink] = field(default_factory=frozenset)
    # Metadata
    ixp_asns: frozenset[int] = field(default_factory=frozenset)
    input_clique_asns: frozenset[int] = field(default_factory=frozenset)
    # You can optionally add diagram ranks for graphviz here
    # By default, it just uses the propagation ranks
    diagram_ranks: Optional[tuple[tuple[int, ...], ...]] = None

    @property
    def asns(self) -> list[int]:
        asns: list[int] = []
        for link_set in self.link_sets:
            for link in link_set:
                asns.extend(link.asns)
        return list(sorted(set(asns)))

    @property
    def link_sets(self) -> tuple[set[Link], ...]:
        """Returns all the link sets

        This way this variable is not hardcoded elsewhere
        so that if we add more links we can just change this list
        """

        return (self.customer_provider_links, self.peer_links)
