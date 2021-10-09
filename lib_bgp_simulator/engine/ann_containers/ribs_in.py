from collections import defaultdict, namedtuple
from dataclasses import dataclass

from .. import bgp_as# import BGPAS
from ...announcement import Announcement
from ...enums import Relationships



AnnInfo = namedtuple("AnnInfo", ["unprocessed_ann", "recv_relationship"])


class RIBsIn:
    """Incomming announcements for a BGP AS

    neighbor: {prefix: (announcement, relationship)}
    """

    __slots__ = ["_info"]

    def __init__(self):
        self._info = defaultdict(dict)

    def get_unprocessed_ann_recv_rel(self, neighbor, prefix):
        assert isinstance(neighbor, int)
        assert isinstance(prefix, str)
        return self._info[neighbor].get(prefix)

    def add_unprocessed_ann(self, unprocessed_ann: Announcement, recv_relationship: Relationships):
        assert isinstance(unprocessed_ann, Announcement)
        ann = unprocessed_ann
        self._info[ann.as_path[0]][ann.prefix] = AnnInfo(unprocessed_ann=unprocessed_ann,
                                                       recv_relationship=recv_relationship)

    def get_ann_infos(self, prefix):
        for prefix_ann_info in self._info.values():
            yield prefix_ann_info.get(prefix, (None, None))

    def remove_entry(self, neighbor, prefix):
        assert isinstance(neighbor, int)
        assert isinstance(prefix, str)

        del self._info[neighbor][prefix]
