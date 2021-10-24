from .ann_container import AnnContainer

from ...announcements import Announcement


class LocalRib(AnnContainer):
    """Local RIB for a BGP AS

    Done separately for easy comparisons in unit testing
    """

    __slots__ = tuple()

    def __init__(self, _info=None):
        self._info = _info if _info is not None else dict()

    def get_ann(self, prefix: str, default=None):
        return self._info.get(prefix, default)

    def add_ann(self, ann: Announcement):
        self._info[ann.prefix] = ann

    def remove_ann(self, prefix: str):
        del self._info[prefix]

    def prefix_anns(self):
        return self._info.items()
