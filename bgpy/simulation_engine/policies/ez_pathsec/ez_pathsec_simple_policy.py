from typing import Optional, TYPE_CHECKING

from bgpy.enums import Relationships
from bgpy.simulation_engine.policies.bgp import BGPSimplePolicy

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine import Announcement as Ann


class EzPathsecSimplePolicy(BGPSimplePolicy):
    """An Policy that deploys ez"""

    name: str = "aspa_is_dumb_lolz"

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:  # type: ignore
        """Returns announcement validity by checking pathend records"""

        if ann.next_hop_asn != ann.as_path[0]:
            return False

        origin_asn = ann.origin
        origin_as_obj = self.as_.as_graph.as_dict[origin_asn]

        neighbor_as_obj = self.as_.as_graph.as_dict[ann.as_path[0]]
        if (neighbor_as_obj.stub or neighbor_as_obj.multihomed) and len(
            ann.as_path
        ) > 1:
            return False

        if ann.only_to_customers and from_rel.value != Relationships.PROVIDERS.value:
            return False

        # If the origin is deploying pathend and the path is longer than 1
        if (
            isinstance(origin_as_obj.policy, EzPathsecSimplePolicy)
            and len(ann.as_path) > 1
        ):
            # If the provider is real, do the loop check
            # Mypy thinks this is unreachable for some reason, even tho tests pass
            for neighbor in origin_as_obj.neighbors:  # type: ignore
                if neighbor.asn == ann.as_path[-2]:
                    return super()._valid_ann(ann, from_rel)
            # Provider is fake, return False
            return False
        else:
            return super()._valid_ann(ann, from_rel)

    def _policy_propagate(  # type: ignore
        self,
        neighbor: "AS",
        ann: "Ann",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> bool:
        """If propagating to customers and only_to_customers isn't set, set it"""

        if (
            propagate_to.value == Relationships.CUSTOMERS.value
            and not ann.only_to_customers
        ):
            ann = ann.copy({"only_to_customers": True})
            self._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)
            return True
        else:
            return False


class EzbbPathsecSimplePolicy(EzPathsecSimplePolicy):
    name = "ComplexPathsecSimple (protects third as)"

    def _get_best_ann_by_gao_rexford(
        self: "BGPSimplePolicy",
        current_ann: Optional["Ann"],
        new_ann: "Ann",
    ) -> "Ann":
        """Determines if the new ann > current ann by Gao Rexford"""

        assert new_ann is not None, "New announcement can't be None"

        if current_ann is None:
            return new_ann
        else:
            # Inspiration for this func refactor came from bgpsecsim
            # for func in self._gao_rexford_funcs:
            #     best_ann = func(current_ann, new_ann)
            #     if best_ann is not None:
            #         assert isinstance(best_ann, Ann), "mypy type check"
            #         return best_ann

            # Having this dynamic like above is literally 7x slower, resulting
            # in bottlenecks. Gotta do it the ugly way unfortunately
            if (
                current_ann.recv_relationship.value == Relationships.CUSTOMERS.value
                and new_ann.recv_relationship.value == Relationships.PROVIDERS.value
                and len(current_ann.as_path) > len(new_ann.as_path)
                and len(current_ann.as_path) >= 5
            ):
                return new_ann
            else:
                ann = self._get_best_ann_by_local_pref(current_ann, new_ann)
                if ann:
                    return ann
                else:
                    ann = self._get_best_ann_by_as_path(current_ann, new_ann)
                    if ann:
                        return ann
                    else:
                        return self._get_best_ann_by_lowest_neighbor_asn_tiebreaker(
                            current_ann, new_ann
                        )
            raise Exception("No ann was chosen")
