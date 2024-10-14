from typing import cast

from .link import Link


class PeerLink(Link):
    """Stores the info for a peer link"""

    def __init__(self, peer1_asn: int, peer2_asn: int):
        """Saves the link info"""

        self.__peer_asns: tuple[int, int] = cast(
            tuple[int, int], tuple(sorted([int(peer1_asn), int(peer2_asn)]))
        )
        super(PeerLink, self).__init__(peer1_asn, peer2_asn)

    def __hash__(self) -> int:
        """Hashes used in sets

        NOTE: python disables hash if __eq__ is defined so you MUST explicitly redef
        """

        return hash(self.asns)

    def __eq__(self, other) -> bool:
        if isinstance(other, PeerLink):
            return self.peer_asns == other.peer_asns
        else:
            return NotImplemented

    @property
    def peer_asns(self) -> tuple[int, int]:
        """Returns peer asns. Done this way for immutability/hashing"""

        return self.__peer_asns

    @property
    def asns(self) -> tuple[int, ...]:
        """Returns asns associated with this link"""

        return tuple(sorted(self.__peer_asns))
