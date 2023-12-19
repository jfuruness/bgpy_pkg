from .link import Link


class PeerLink(Link):
    """Stores the info for a peer link"""

    def __init__(self, peer1_asn: int, peer2_asn: int):
        """Saves the link info"""

        self.__peer_asns: tuple[int, int] = tuple(
            sorted([int(peer1_asn), int(peer2_asn)])
        )  # type: ignore
        super(PeerLink, self).__init__()

    @property
    def peer_asns(self) -> tuple[int, int]:
        """Returns peer asns. Done this way for immutability/hashing"""

        return self.__peer_asns

    @property
    def asns(self) -> tuple[int, ...]:
        """Returns asns associated with this link"""

        return tuple(sorted(self.__peer_asns))  # type: ignore
