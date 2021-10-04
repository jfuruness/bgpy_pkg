from .bgp_policy import BGPPolicy

from ..enums import Relationships, ROAValidity
from ..announcement import Announcement as Ann


class ROVPolicy(BGPPolicy):
    __slots__ = []

    name = "ROV"

    def _valid_ann(policy_self, self, ann, *args, **kwargs):
        if ann.roa_validity == ROAValidity.INVALID:
            return False
        else:
            return super(ROVPolicy, policy_self)._valid_ann(self, ann, *args, **kwargs)
