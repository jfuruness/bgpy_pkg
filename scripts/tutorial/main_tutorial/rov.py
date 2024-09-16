from bgpy.simulation_engine import BGP
from bgpy.simulation_engine import Announcement as Ann
from bgpy.shared.enums import Relationships

class ROV(BGP):
    """An Policy that deploys ROV"""

    name: str = "TutorialROV"

    def _valid_ann(self, ann: Ann, recv_rel: Relationships) -> bool:
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
            return super(ROV, self)._valid_ann(ann, recv_rel)
