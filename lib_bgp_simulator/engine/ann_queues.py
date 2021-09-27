from collections import defaultdict


class AnnQueue(defaultdict):
    """Adj_RIBs_In for a BGP AS

    Map neighbors to the announcements they sent to this AS.
    {neighbor: {prefix: list_of_ann}}
    """

    __slots__ = []

    def __init__(self, *args, **kwargs):
        super(AnnQueue, self).__init__(lambda : defaultdict(list), *args, **kwargs)

    @property
    def announcements(self):
        """Returns all announcements in the q"""

        for neighbor, prefix_ann_dict in self.items():
            for ann_list in prefix_ann_dict.values():
                for ann in ann_list:
                    yield ann

    def assert_eq(self, other):
        """Checks equality of local ribs using prefix, origin, as_path, time"""

        raise NotImplementedError


class RecvQueue(AnnQueue):
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement_list}
    """

    __slots__ = []


class SendQueue(AnnQueue):
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement_list}
    """

    __slots__ = []
