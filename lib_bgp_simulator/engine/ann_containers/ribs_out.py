from collections import defaultdict
from typing import Optional

from ...announcements import Announcement as Ann


class RIBsOut:
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement}
    """

    __slots__ = "_info",

    def __init__(self):
        self._info = defaultdict(dict)

    def __eq__(self, other):
        # Remove this after updating the system tests
        if isinstance(other, dict):
            return self._info == other
        elif isinstance(other, RIBsOut):
            return self._info == other._info
        else:
            raise NotImplementedError

    def get_ann(self, neighbor_asn: int, prefix: str) -> Optional[Ann]:
        return self._info[neighbor_asn].get(prefix)

    def add_ann(self, neighbor_asn: int, ann: Ann):
        self._info[neighbor_asn][ann.prefix] = ann

    def remove_entry(self, neighbor_asn: int, prefix: str):
        del self._info[neighbor_asn][prefix]

    def neighbors(self):
        return self._info.keys()
