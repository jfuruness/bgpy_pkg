from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships
from .asra import ASRA

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ASRAD(ASRA):
    name = "ASRAD"

    @property
    def UP_SLACK(self) -> int:
        return 0

    @property
    def DOWN_SLACK(self) -> int:
        return 0

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:
        # 1) run ASPA + ASRA first
        if not super()._valid_ann(ann, from_rel):
            return False
        elif not self.asrad_valid(ann, from_rel):
            return False
        else:
            return True

    def asrad_valid(self, ann: "Ann", from_rel: Relationships) -> bool:
        as_graph = self.as_.as_graph
        rpath = ann.as_path[::-1]

        # Case 1: Recieved from a customer
        # For any AS along the path that is adopting
        # If the total AS Path length is greater than the max height reject
        # Otherwise if all are valid, return valid
        if from_rel == Relationships.CUSTOMER:
            for i, asn in enumerate(rpath):
                as_obj = as_graph[asn]
                if (
                    isinstance(as_obj.policy, ASRAD)
                    and len(rpath) - i - self.UP_SLACK > as_obj.max_height
                ):
                    return False
            return True

        # Case 2: Recieved from a peer
        # Same as the customer, plus one to account for peering
        elif from_rel == Relationships.PEER:
            for i, asn in enumerate(rpath):
                as_obj = as_graph[asn]
                if (
                    isinstance(as_obj.policy, ASRAD)
                    and len(rpath) - i - self.UP_SLACK - 1 > as_obj.max_height
                ):
                    return False
            return True

        # Case 3: Received from a provider
        # You need to check for your AS, and every other combo of AS:
        #   when both ASes are adopting...
        #       your max height + their max height + 1 for peer + up slack
        #       should be greater than the length of the path between those
        #       two ASes
        #
        #   Additionally:
        #   You should be able to make the above stricter given a range
        #   for the peak information... how?
        #
        #   Additionally:
        #   You should be able to repeat the above with the depth/downpath
        elif from_rel == Relationships.PROVIDER:
            return True
        else:
            raise NotImplementedError("Relationship not accounted for")

        # Case 4:
        # Somehow utilizing customer and peer separation information?


class ASRAD1(ASRAD):
    name = "ASRAD1"
    UP_SLACK = 1
    DOWN_SLACK = 1


class ASRAD2(ASRAD):
    name = "ASRAD2"
    UP_SLACK = 2
    DOWN_SLACK = 2
