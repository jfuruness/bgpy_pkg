from .ribs import RibsIn, RibsOut

class RecvQueue(RibsIn):
    """Incomming announcements for a BGP AS

    Done separately for easy comparisons in unit testing

    neighbor: {prefix: announcement_list}
    """

    __slots__ = []

class SendQueue(RibsOut):
    """Incomming announcements for a BGP AS

    Done separately for easy comparisons in unit testing

    neighbor: {prefix: announcement_list}
    """

    __slots__ = []
