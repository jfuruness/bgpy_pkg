from .bgp_policy import BGPPolicy

from ..enums import Relationships, ROAValidity
from ..announcement import Announcement as Ann


class ROVPolicy(BGPPolicy):
    __slots__ = []

    name = "ROV"

    def _get_priority(policy_self, ann: Ann, recv_relationship: Relationships):
        """Assigns the priority to an announcement according to Gao Rexford"""

        if ann.roa_validity == ROAValidity.INVALID:
            # -1 is lower than the worst priority
            # So it will never be chosen
            return -1
        #ann.recv_relationship = recv_relationship
        # Document this later
        # Seeded (a bool)
        # Relationship
        # Path length
        # 100 - is to invert the as_path so that longer paths are worse
        assert len(ann.as_path) < 100
        # We subtract an extra 1 because this is still the old ann
        return recv_relationship.value + 100 - len(ann.as_path) - 1
