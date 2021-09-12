from collections import defaultdict

from .local_rib import LocalRib


class IncomingAnns(defaultdict):
    """Incomming announcements for a BGP AS

    Done separately for easy comparisons in unit testing

    prefix: announcement_list

    Later we can add functionality to this class for ez testing
    """

    __slots__ = []

    def __init__(self, *args, **kwargs):
        super(IncomingAnns, self).__init__(list, *args, **kwargs)

    def assert_eq(self):
        raise NotImplementedError
