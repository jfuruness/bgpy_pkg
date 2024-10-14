from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships
from bgpy.simulation_engine.policies.rov import ROV

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ASPA(ROV):
    """A Policy that deploys ASPA and ASPA Records

    We adopt from ROV since deploying ASPA makes no sense without ROV

    We experimented with adding a cache to the provider_check
    but this has a negligible impact on performance

    Removing the path reversals sped up performance by about 5%
    but made the code a lot less readable and deviated from the RFC,
    so we decided to forgo those as well

    This is now up to date with the V18 proposal
    """

    name: str = "ASPA"

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:
        """Returns False if from peer/customer when aspa is set"""

        assert len(set(ann.as_path)) == len(ann.as_path), "We deal with prepending"

        # Note: This first if check has to be removed if you want to implement
        # route server to RS-Client behaviour
        if not self._next_hop_valid(ann):
            return False
        # Most ASes recieve anns from providers (moved here for speed)
        elif from_rel.value == Relationships.PROVIDERS.value:
            return self._downstream_check(ann, from_rel)
        elif from_rel.value in (
            Relationships.CUSTOMERS.value,
            Relationships.PEERS.value,
        ):
            return self._upstream_check(ann, from_rel)
        else:
            raise NotImplementedError("Should never reach here")

    def _next_hop_valid(self, ann: "Ann") -> bool:
        """Ensures the next hop is the first ASN in the AS-Path

        This behavior would need to be modified for route servers
        """

        return ann.next_hop_asn == ann.as_path[0]

    def _upstream_check(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """ASPA upstream check"""

        # Upstream check
        if len(ann.as_path) == 1:
            return super()._valid_ann(ann, from_rel)
        # For every adopting ASPA AS in the path,
        # The next ASN in the path must be in their providers list
        # Since this is checking from customers

        # 4. If max_up_ramp < N, the procedure halts with the outcome "Invalid".
        elif self._get_max_up_ramp_length(ann) < len(ann.as_path):
            return False

        # ASPA valid or unknown
        return super()._valid_ann(ann, from_rel)

    def _get_max_up_ramp_length(self, ann: "Ann") -> int:
        """See desc

        Determine the maximum up-ramp length as I, where I is the minimum
        index for which authorized(A(I), A(I+1)) returns "Not Provider+".  If
        there is no such I, the maximum up-ramp length is set equal to the
        AS_PATH length N.  This parameter is defined as max_up_ramp

        The up-ramp starts at AS(1) and each hop AS(i) to AS(i+1) represents
        Customer and Provider peering relationship. [i.e they reverse the path]
        """

        reversed_path = ann.as_path[::-1]

        for i in range(len(reversed_path) - 1):
            if not self._provider_check(reversed_path[i], reversed_path[i + 1]):
                return i + 1
        return len(ann.as_path)

    def _downstream_check(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """ASPA downstream check"""

        # 4. If max_up_ramp + max_down_ramp < N,
        # the procedure halts with the outcome "Invalid".
        max_up_ramp = self._get_max_up_ramp_length(ann)
        max_down_ramp = self._get_max_down_ramp_length(ann)
        if max_up_ramp + max_down_ramp < len(ann.as_path):
            return False

        # ASPA Valid or Unknown (but not invalid)
        return super()._valid_ann(ann, from_rel)

    def _get_max_down_ramp_length(self, ann: "Ann") -> int:
        """See desc

        Similarly, the maximum down-ramp length can be determined as N - J +
        1 where J is the maximum index for which authorized(A(J), A(J-1))
        returns "Not Provider+".  If there is no such J, the maximum down-
        ramp length is set equal to the AS_PATH length N.  This parameter is
        defined as max_down_ramp.

        In the down-ramp, each pair AS(j) to
        AS(j-1) represents Customer and Provider peering relationship
        """

        reversed_path = ann.as_path[::-1]

        # We want the max J, so start at the end of the reversed Path
        # This is the most efficient way to traverse this
        for i in range(len(reversed_path) - 1, 0, -1):
            if not self._provider_check(reversed_path[i], reversed_path[i - 1]):
                # Must add one due to zero indexing in python, vs 1 indexing in RFC
                J = i + 1
                return len(reversed_path) - J + 1
        return len(ann.as_path)

    def _provider_check(self, asn1: int, asn2: int) -> bool:
        """Returns False if asn2 is not in asn1's provider_asns, AND asn1 adopts ASPA

        This also essentially can take the place of the "hop check" listed in
        ASPA RFC section 5 in ASPA v16
        or in ASPAv18 it takes the place of the provider auth func

        False indicates Not Provider+
        True indicates No Attestation or Provider+
        """

        cur_as_obj = self.as_.as_graph.as_dict[asn1]
        if isinstance(cur_as_obj.policy, ASPA):
            next_as_obj = self.as_.as_graph.as_dict[asn2]
            if next_as_obj.asn not in cur_as_obj.provider_asns:
                return False
        return True
