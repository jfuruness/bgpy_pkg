from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships
from .asra_b_clp import ASRA_B_CLP
from .aspa import ASPA

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ASRAUS(ASRA_B_CLP):
    name = "ASRA Ultra Simple"

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:
        # 1) run ASPA + ASRA first
        if not super()._valid_ann(ann, from_rel):
            return False
        elif not self.asra_ultra_simple_valid(ann, from_rel):
            return False
        else:
            return True

    def asra_ultra_simple_valid(self, ann: "Ann", from_rel: Relationships) -> bool:
        as_graph = self.as_.as_graph

        # Case 1: Recieved from a customer
        # All ASes except for origin can not be edge
        if from_rel == Relationships.CUSTOMERS:
            for i, asn in enumerate(ann.as_path):
                as_obj = as_graph.as_dict[asn]
                if (
                    # Checking for stubs
                    (
                        isinstance(as_obj.policy, ASRAUS)
                        and (as_obj.stub or as_obj.multihomed)
                        and not asn == ann.origin
                    )
                    # Peerlock lite
                    or (
                        isinstance(as_obj.policy, ASRAUS)
                        and (as_obj.input_clique)
                    )
                ):
                    return False
            return True
        # Same as customers, except tier-1 is allowed to be directly next to AS
        elif from_rel == Relationships.PEERS:
            for i, asn in enumerate(ann.as_path):
                as_obj = as_graph.as_dict[asn]
                if (
                    # Checking for stubs
                    (
                        isinstance(as_obj.policy, ASRAUS)
                        and (as_obj.stub or as_obj.multihomed)
                        and not asn == ann.origin
                    )
                    # Peerlock lite
                    or (
                        isinstance(as_obj.policy, ASRAUS)
                        and (as_obj.input_clique)
                        and i != 0  # Directly next to AS is allowed
                    )
                ):
                    return False
            return True
        # Same as the customer, except you can have a t1 in the path so long as they aren't split
        elif from_rel == Relationships.PROVIDERS:
            for i, asn in enumerate(ann.as_path):
                as_obj = as_graph.as_dict[asn]
                if (
                    # Checking for stubs
                    (
                        isinstance(as_obj.policy, ASRAUS)
                        and (as_obj.stub or as_obj.multihomed)
                        and not asn == ann.origin
                    )
                ):
                    return False
            # Check for tier-1 separation
            # I don't think peerlock-lite does this....
            seen_tier_1 = self.as_.input_clique
            prev_tier_1 = self.as_.input_clique
            for i, asn in enumerate(ann.as_path):
                as_obj = as_graph.as_dict[asn]
                if as_obj.input_clique:
                    if seen_tier_1 and not prev_tier_1:
                        return False
                    else:
                        seen_tier_1 = True
                        prev_tier_1 = True
                else:
                    prev_tier_1 = False
            return True
        else:
            raise NotImplementedError("Relationship not accounted for")
