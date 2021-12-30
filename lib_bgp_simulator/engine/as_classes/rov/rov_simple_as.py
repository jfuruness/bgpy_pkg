from ..bgp import BGPSimpleAS

from ....announcements import Announcement as Ann
from ....enums import ROAValidity


class ROVSimpleAS(BGPSimpleAS):
    __slots__ = tuple()

    name = "ROVSimple"

    def _valid_ann(self, ann: Ann, *args, **kwargs) -> bool:
        if ann.invalid_by_roa:
            return False
        else:
            return super(ROVSimpleAS, self)._valid_ann(ann, *args, **kwargs)
