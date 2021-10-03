from collections import defaultdict


class SendQueue:
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement_list}
    """

    __slots__ = ["_info"]

    def __init__(self):
        self._info = defaultdict(lambda: defaultdict(list))

    def add_ann(self, neighbor, ann, prefix=None):
        assert isinstance(neighbor, int)
        assert isinstance(ann, Announcement)
        assert prefix is None or isinstance(prefix, str)

        prefix = prefix if prefix is not None else ann.prefix

        self._info[neighbor][prefix].append(ann)
