from typing import TYPE_CHECKING, Callable

from bgpy.enums import Relationships
from bgpy.simulation_engine.policies.rov import ROV

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ASPA(ROV):
    """A Policy that deploys ASPA

    We adopt from ROV since deploying ASPA makes no sense without ROV

    We experimented with adding a cache to the provider_check
    but this has a negligible impact on performance

    Removing the path reversals sped up performance by about 5%
    but made the code a lot less readable and deviated from the RFC,
    so we decided to forgo those as well
    """

    name: str = "ASPA"

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:  # type: ignore
        """Returns False if from peer/customer when aspa is set"""

        assert len(set(ann.as_path)) == len(ann.as_path), "We deal with prepending"

        # Note: This first if check has to be removed if you want to implement
        # route server to RS-Client behaviour
        if ann.next_hop_asn != ann.as_path[0]:
            return False
        elif from_rel.value in (
            Relationships.CUSTOMERS.value,
            Relationships.PEERS.value,
        ):
            return self._upstream_check(ann, from_rel)
        elif from_rel.value == Relationships.PROVIDERS.value:
            return self._downstream_check(ann, from_rel)
        else:
            raise NotImplementedError("Should never reach here")

    def _upstream_check(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """ASPA upstream check"""

        # Upstream check
        if len(ann.as_path) == 1:
            return super()._valid_ann(ann, from_rel)
        else:
            # For every adopting ASPA AS in the path,
            # The next ASN in the path must be in their providers list

            # 4. If max_up_ramp < N, the procedure halts with the outcome "Invalid".
            if self.get_max_up_ramp_length(ann) < len(ann.as_path):
                return False

            # No need to actually verify the min_up_ramp as we accept Unknown announcements
            # 5. If min_up_ramp < N, the procedure halts with the outcome "Unknown".
            if self.get_min_up_ramp_length(ann) < len(ann.as_path):
                # Valid as we do not invalidate Unknown announcements
                return super()._valid_ann(ann, from_rel)

        # Actually ASPA-valid
        return super()._valid_ann(ann, from_rel)

    def get_max_up_ramp_length(self, ann: "Ann") -> int:
        """Upstream ramp length function, responsible for the qualification into either Invalid or Unknown/Valid"""
        reversed_path = ann.as_path[::-1]
        uppercase_i = iterate_check_func_over_asn_path(
            reversed_path, self._provider_or_peer_check
        )

        # If there is no such I, the maximum up-ramp length is set equal to the AS_PATH length N
        if uppercase_i == len(reversed_path) - 1:
            max_up_ramp = len(reversed_path)
        else:
            max_up_ramp = uppercase_i

        return max_up_ramp

    def get_min_up_ramp_length(self, ann: "Ann") -> int:
        """Upstream ramp length function, responsible for the qualification into either Unknown or Valid"""
        reversed_path = ann.as_path[::-1]
        uppercase_i = iterate_check_func_over_asn_path(
            reversed_path, self._provider_check
        )
        # If there is no such I, the AS_PATH consists of only "Provider+" pairs;
        # so the minimum up-ramp length is set equal to the AS_PATH length N.
        if uppercase_i == len(reversed_path) - 1:
            min_up_ramp = len(reversed_path)
        else:
            min_up_ramp = uppercase_i

        return min_up_ramp

    def _downstream_check(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """ASPA downstream check"""
        # downstream check

        # 4. If max_up_ramp + max_down_ramp < N, the procedure halts with the outcome "Invalid".
        max_up_ramp = self.get_max_up_ramp_length(ann)
        if max_up_ramp + self.get_max_down_ramp_length(ann) < len(ann.as_path):
            return False

        # 5. If min_up_ramp + min_down_ramp < N, the procedure halts with the outcome "Unknown".
        min_up_ramp = self.get_min_up_ramp_length(ann)
        if min_up_ramp + self.get_min_down_ramp_length(ann) < len(ann.as_path):
            return super()._valid_ann(ann, from_rel)

        # Actually ASPA valid
        return super()._valid_ann(ann, from_rel)

    def get_max_down_ramp_length(self, ann: "Ann") -> int:
        """Downstream ramp length function, responsible for the qualification into either Invalid or Unknown/Valid
        in combination with the maximum upstream ramp length results"""
        as_path = ann.as_path
        uppercase_j = iterate_check_func_over_asn_path(
            as_path, self._provider_or_peer_check
        )
        # If there is no such J, the maximum down-ramp length is set equal to the AS_PATH length N
        if uppercase_j == len(as_path) - 1:
            max_down_ramp = len(as_path)
        else:
            max_down_ramp = uppercase_j
        return max_down_ramp

    def get_min_down_ramp_length(self, ann: "Ann") -> int:
        """Downstream ramp length function, responsible for the qualification into either Unknown or Valid
        in combination with the minimum upstream ramp length results"""
        as_path = ann.as_path
        uppercase_j = iterate_check_func_over_asn_path(as_path, self._provider_check)

        # If there is no such J, the minimum down-ramp length is set equal to the AS_PATH length N.
        if uppercase_j == len(as_path) - 1:
            min_down_ramp = len(as_path)
        else:
            min_down_ramp = uppercase_j

        return min_down_ramp

    def _provider_check(self, asn1: int, asn2: int) -> bool:
        """Returns True if asn2 is the provider of asn1. If asn1 does not adopt
        ASPA, the function returns False. This function equals Provider+ from the RFC

        This function is used to establish the length of the min_up_ramp
        and min_down_ramp
        """
        cur_as_obj = self.as_.as_graph.as_dict[asn1]
        if isinstance(cur_as_obj.policy, ASPA):
            next_as_obj = self.as_.as_graph.as_dict[asn2]
            return next_as_obj.asn in cur_as_obj.provider_asns
        else:
            return False

    def _provider_or_peer_check(self, asn1: int, asn2: int) -> bool:
        """Returns False if asn2 is not in asn1's provider_asns, AND asn1 adopts ASPA

        This function is used to establish the length of the max_up_ramp
        and max_down_ramp and its boolean True equals "No Attestation" or "Provider+"
        """

        cur_as_obj = self.as_.as_graph.as_dict[asn1]
        if not isinstance(cur_as_obj.policy, ASPA):
            return True
        else:
            next_as_obj = self.as_.as_graph.as_dict[asn2]
            if next_as_obj.asn not in cur_as_obj.provider_asns:
                return False
        return True


def iterate_check_func_over_asn_path(
    reversed_path: tuple[int, ...], check_func: Callable
) -> int:
    """Utility function for ASPA as not to have too much code repetition and to keep
    the path iteration logic unified"""
    current_checked_length = 0
    for i in range(len(reversed_path) - 1):
        if check_func(reversed_path[i], reversed_path[i + 1]):
            current_checked_length += 1
        else:
            break
    return current_checked_length
