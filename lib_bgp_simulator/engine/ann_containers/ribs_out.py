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

    def get_ann(self, neighbor_asn: int, prefix: str) -> Optional[Ann]:
        return self._info[neighbor_asn].get(prefix)

    def add_ann(self, neighbor_asn: int, ann: Ann):
        self._info[neighbor_asn][ann.prefix] = ann

    def remove_entry(self, neighbor_asn: int, prefix: str):
        del self._info[neighbor_asn][prefix]

    def neighbors(self):
        return self._info.keys()
