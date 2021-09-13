from .bgp_policy import BGPPolicy

from ..enums import Relationships, ROAValidity
from ..announcement import Announcement as Ann


class ROVPolicy(BGPPolicy):
    __slots__ = []

    name = "ROV"

    def _new_ann_is_better(policy_self, self, deep_ann, shallow_ann, recv_relationship: Relationships):

        if shallow_ann.roa_validity == ROAValidity.INVALID:
            return False

        return super(ROVPolicy, policy_self)._new_ann_is_better(self, deep_ann, shallow_ann, recv_relationship)
