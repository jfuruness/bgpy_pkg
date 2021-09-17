from collections import defaultdict


class Ribs(defaultdict):
    """Adj_RIBs_In for a BGP AS

    Map neighbors to the announcements they sent to this AS.
    {neighbor: {prefix: ann}}
    """

    __slots__ = []

    def __init__(self, *args, **kwargs):
        super(Ribs, self).__init__(dict, *args, **kwargs)

    def assert_eq(self, other):
        """Checks equality of local ribs using prefix, origin, as_path, time"""

        raise NotImplementedError


class RibsIn(Ribs):
    """Adj_RIBs_In for a BGP AS

    Map neighbors to the announcements they sent to this AS.
    """

    __slots__ = []


class RibsOut(Ribs):
    """Adj_RIBs_Out for a BGP AS

    Map neighbors to the announcements they are being sent from this AS.
    """

    __slots__ = []
