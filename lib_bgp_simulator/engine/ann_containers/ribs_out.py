from collections import defaultdict

from ...announcements import Announcement


class RIBsOut:
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement}
    """

    __slots__ = "_info",

    def __init__(self):
        self._info = defaultdict(dict)

    def get_ann(self, neighbor, prefix):
        assert isinstance(neighbor, int)
        assert isinstance(prefix, str)
        return self._info[neighbor].get(prefix)

    def add_ann(self, neighbor_asn: int, ann: Announcement):
        assert isinstance(neighbor_asn, int)
        assert isinstance(ann, Announcement)

        self._info[neighbor_asn][ann.prefix] = ann

    def remove_entry(self, neighbor_asn, prefix):
        assert isinstance(neighbor_asn, int)
        assert isinstance(prefix, str)
        del self._info[neighbor_asn][prefix]

    def neighbors(self):
        return self._info.keys()
