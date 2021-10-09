from collections import defaultdict, namedtuple
from dataclasses import dataclass

from .. import bgp_as# import BGPAS
from ...announcement import Announcement
from ...enums import Relationships



class RIBsOut:
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement}
    """

    __slots__ = ["_info"]

    def __init__(self):
        self._info = defaultdict(dict)

    def get_ann(self, neighbor, prefix):
        assert isinstance(neighbor, int)
        assert isinstance(prefix, str)
        return self._info[neighbor].get(prefix)

    def add_ann(self, neighbor_asn: int, ann: Announcement, prefix=None):
        assert isinstance(neighbor_asn, int)
        assert isinstance(ann, Announcement)
        assert prefix is None or isinstance(prefix, str)

        prefix = prefix if prefix is not None else ann.prefix

        self._info[neighbor_asn][prefix] = ann

    def remove_entry(self, neighbor_asn, prefix):
        assert isinstance(neighbor_asn, int)
        assert isinstance(prefix, str)
        del self._info[neighbor_asn][prefix]

    def neighbors(self):
        return self._info.keys()        
