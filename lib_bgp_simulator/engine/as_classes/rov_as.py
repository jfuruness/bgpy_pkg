from .bgp_as import BGPAS

from ...announcements import Announcement as Ann
from ...enums import ROAValidity


class ROVAS(BGPAS):
    __slots__ = tuple()

    name = "ROV"

    def _valid_ann(self, ann: Ann, *args, **kwargs) -> bool:
        if ann.roa_validity == ROAValidity.INVALID:
            return False
        else:
            return super(ROVAS, self)._valid_ann(ann, *args, **kwargs)
