from .bgp_policy import BGPPolicy

from ..enums import Relationships, ROAValidity
from ..announcement import Announcement as Ann


class ROVPolicy(BGPPolicy):
    __slots__ = []

    name = "ROV"

    def _valid_ann(policy_self, self, ann, **kwargs):
        if ann.roa_validity == ROAValidity.INVALID:
            return False
        else:
            return super(ROVPolicy, policy_self)._valid_ann(self, ann, **kwargs)

    def _new_ann_is_better(policy_self, self, deep_ann, shallow_ann, recv_relationship: Relationships):
        # Should have been dropped earlier by _valid_ann
        assert shallow_ann.roa_validity == ROAValidity.VALID

        return super(ROVPolicy, policy_self)._new_ann_is_better(self, deep_ann, shallow_ann, recv_relationship)
