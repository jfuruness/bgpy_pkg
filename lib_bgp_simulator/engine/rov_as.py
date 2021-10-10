from .bgp_as import BGPAS

from ..enums import Relationships, ROAValidity
from ..announcement import Announcement as Ann


class ROVAS(BGPAS):
    __slots__ = []

    name = "ROV"

    def _valid_ann(self, ann, *args, **kwargs):
        if ann.roa_validity == ROAValidity.INVALID:
            return False
        else:
            return super(ROVAS, self)._valid_ann(ann, *args, **kwargs)
