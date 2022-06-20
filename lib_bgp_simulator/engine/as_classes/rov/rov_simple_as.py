from ..bgp import BGPSimpleAS

from ....announcement import Announcement as Ann


class ROVSimpleAS(BGPSimpleAS):
    """An AS that deploys ROV"""

    __slots__ = ()

    name = "ROVSimple"

    def _valid_ann(self, ann: Ann, *args, **kwargs) -> bool:
        """Returns announcement validity

        Returns false if invalid by roa,
        otherwise uses standard BGP (such as no loops, etc)
        to determine validity
        """

        # Invalid by ROA is not valid by ROV
        if ann.invalid_by_roa:
            return False
        # Use standard BGP to determine if the announcement is valid
        else:
            return super(ROVSimpleAS, self)._valid_ann(ann, *args, **kwargs)
