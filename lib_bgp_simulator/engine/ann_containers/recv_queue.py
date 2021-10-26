from collections import defaultdict

from .ann_container import AnnContainer

from ...announcements import Announcement


class RecvQueue(AnnContainer):
    """Adj_RIBs_In for a BGP AS

    Map prefixes to anns sent
    {prefix: list_of_ann}
    """

    __slots__ = tuple()

    def __init__(self, _info=None):
        self._info = _info if _info is not None else defaultdict(list)

    def add_ann(self, ann: Announcement):
        self._info[ann.prefix].append(ann)

    def prefix_anns(self):
        return self._info.items()

    def get_ann_list(self, prefix):
        return self._info.get(prefix, [])
