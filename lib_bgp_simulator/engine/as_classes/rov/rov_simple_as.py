from ..bgp import BGPSimpleAS

from ....announcements import Announcement as Ann
from ....enums import ROAValidity


class ROVSimpleAS(BGPSimpleAS):
    __slots__ = tuple()

    name = "ROVSimple"

    def _valid_ann(self, ann: Ann, *args, **kwargs) -> bool:
        if ann.roa_validity == ROAValidity.INVALID:
            return False
        else:
            return super(ROVAS, self)._valid_ann(ann, *args, **kwargs)
