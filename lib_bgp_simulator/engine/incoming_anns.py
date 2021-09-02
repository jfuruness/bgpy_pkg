from .local_rib import LocalRib


class IncomingAnns(LocalRib):
    """Incomming announcements for a BGP AS

    Done separately for easy comparisons in unit testing

    prefix: announcement_list

    Later we can add functionality to this class for ez testing
    """

    __slots__ = []
