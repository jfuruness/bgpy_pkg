from abc import ABC, abstractmethod
from typing import Any


class Link(ABC):
    """Contains a relationship link in a BGP topology"""

    def __init__(self, asn1: int, asn2: int) -> None:
        # Make sure we have asns
        # Make sure the asns is a tuple
        assert isinstance(self.asns, tuple)
        # Make sure the asns is sorted
        assert tuple(sorted(self.asns)) == self.asns

    def __hash__(self) -> int:
        """Hashes used in sets"""

        return hash(self.asns)

    @abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError

    def __lt__(self, other: Any):
        if isinstance(other, Link):
            return self.__hash__() < other.__hash__()
        else:
            return NotImplemented

    @property
    @abstractmethod
    def asns(self) -> tuple[int, ...]:
        raise NotImplementedError
