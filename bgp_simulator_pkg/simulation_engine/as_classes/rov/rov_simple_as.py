from ..bgp import BGPSimpleAS

from ...announcement import Announcement as Ann


class ROVSimpleAS(BGPSimpleAS):
    """An AS that deploys ROV"""

    name: str = "ROVSimple"

    # mypy doesn't understand that this func is valid
    def _valid_ann(self, ann: Ann, *args, **kwargs) -> bool:  # type: ignore
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
            # Mypy doesn't map superclasses properly
            return super(ROVSimpleAS,  # type: ignore
                         self)._valid_ann(ann, *args, **kwargs)
