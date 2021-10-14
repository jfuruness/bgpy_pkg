from collections import defaultdict

from ...announcement import Announcement


class RecvQueue(defaultdict):
    """Adj_RIBs_In for a BGP AS

    Map neighbors to the announcements they sent to this AS.
    {neighbor: {prefix: list_of_ann}}
    """

    __slots__ = "_info",

    def __init__(self):
        self._info = defaultdict(list)

    def add_ann(self, ann):
        assert isinstance(ann, Announcement)

        self._info[ann.prefix].append(ann)

    def prefix_anns(self):
        return self._info.items()
