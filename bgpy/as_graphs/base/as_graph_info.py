from dataclasses import dataclass, field

from .links import CustomerProviderLink as CPLink
from .links import Link, PeerLink


@dataclass(frozen=True, slots=True)
class ASGraphInfo:
    """Contains information to build a graph"""

    # Links
    customer_provider_links: frozenset[CPLink] = field(default_factory=frozenset)
    peer_links: frozenset[PeerLink] = field(default_factory=frozenset)
    unlinked_asns: frozenset[int] = field(default_factory=frozenset)
    # Metadata
    ixp_asns: frozenset[int] = field(default_factory=frozenset)
    input_clique_asns: frozenset[int] = field(default_factory=frozenset)
    # You can optionally add diagram ranks for graphviz here
    # By default, it just uses the propagation ranks
    diagram_ranks: tuple[tuple[int, ...], ...] = ()

    def __post_init__(self, *args, **kwargs):
        asn_tuples = list()
        for link in self.links:
            asn_tuples.append(link.asns)

        msg = "Shouldn't have a customer-provider that is also a peer!"
        assert len(asn_tuples) == len(set(asn_tuples)), msg

    def __eq__(self, other) -> bool:
        if isinstance(other, ASGraphInfo):
            return self.asns == other.asns
        else:
            return NotImplemented

    @property
    def asns(self) -> list[int]:
        asns: list[int] = []
        for link in self.links:
            asns.extend(link.asns)
        asns.extend(list(self.unlinked_asns))
        return sorted(set(asns))

    @property
    def links(self) -> frozenset[Link]:
        """Returns all the links

        This way this variable is not hardcoded elsewhere
        so that if we add more links we can just change this list
        """

        return frozenset({*self.customer_provider_links, *self.peer_links})
