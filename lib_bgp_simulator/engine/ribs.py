from collections import defaultdict

class RibsIn(defaultdict):
    """Adj_RIBs_In for a BGP AS

    Map neighbors to the announcements they sent to this AS.
    """

    __slots__ = []

    def __init__(self, *args, **kwargs):
        super(RibsIn, self).__init__(lambda : defaultdict(list), *args, **kwargs)

    def assert_eq(self, other):
        """Checks equality of local ribs using prefix, origin, as_path, time"""

        if isinstance(other, RibsIn):
            for asn in self:
                assert self[asn] == other[asn]
        else:
            raise NotImplementedError

    def __str__(self):
        """String method done to turn anns into strings"""

        string = "{"
        for k, v in self.items():
            string += f"{k}: {v}, "
        string += "}"
        return string

class RibsOut(defaultdict):
    """Adj_RIBs_Out for a BGP AS

    Map neighbors to the announcements they are being sent from this AS.
    """

    __slots__ = []

    def __init__(self, *args, **kwargs):
        super(RibsOut, self).__init__(lambda : defaultdict(list), *args, **kwargs)

    def assert_eq(self, other):
        """Checks equality of local ribs using prefix, origin, as_path, time"""

        if isinstance(other, RibsOut):
            for asn in self:
                assert self[asn] == other[asn]
        else:
            raise NotImplementedError

    def __str__(self):
        """String method done to turn anns into strings"""

        string = "{"
        for k, v in self.items():
            string += f"{k}: {v}, "
        string += "}"
        return string
