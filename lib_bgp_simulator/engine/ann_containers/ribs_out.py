from collections import defaultdict
from typing import Optional

from .ann_container import AnnContainer

from ...announcements import Announcement as Ann


class RIBsOut(AnnContainer):
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement}
    """

    __slots__ = tuple()

    def __init__(self, _info=None):
        self._info = _info if _info is not None else defaultdict(dict)

    def get_ann(self, neighbor_asn: int, prefix: str) -> Optional[Ann]:
        return self._info[neighbor_asn].get(prefix)

    def add_ann(self, neighbor_asn: int, ann: Ann):
        self._info[neighbor_asn][ann.prefix] = ann

    def remove_entry(self, neighbor_asn: int, prefix: str):
        del self._info[neighbor_asn][prefix]

    def neighbors(self):
        return self._info.keys()
