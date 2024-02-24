from typing import TYPE_CHECKING

from bgpy.enums import Relationships
from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ASPA(BGP):
    """An Policy that deploys ASPA

    We experimented with adding a cache to the provider_check
    but this has a negligable impact on performance

    Removing the path reversals sped up performance by about 5%
    but made the code a lot less readable and deviated from the RFC
    so we decided to forgo those as well
    """

    name: str = "ASPA"

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:  # type: ignore
        """Returns False if from peer/customer when aspa is set"""

        assert len(set(ann.as_path)) == len(ann.as_path), "We deal with prepending"

        if ann.next_hop_asn != ann.as_path[0]:
            return False
        # If ann.aspa is set, only accept from a provider
        elif from_rel.value in (
            Relationships.CUSTOMERS.value,
            Relationships.PEERS.value,
        ):
            return self._upstream_check(ann, from_rel)
        elif from_rel.value == Relationships.PROVIDERS.value:
            return self._downstream_check(ann, from_rel)
        else:
            raise NotImplementedError("Should never reach here")

    def _upstream_check(self, ann: "Ann", from_rel: Relationships) -> bool:
        """ASPA upstream check"""

        # Upstream check
        if len(ann.as_path) == 1:
            return super()._valid_ann(ann, from_rel)
        else:
            reversed_path = ann.as_path[::-1]  # type: ignore
            # For every adopting ASPA AS in the path,
            # The next ASN in the path must be in their providers list
            for i in range(len(reversed_path) - 1):
                if not self._provider_check(reversed_path[i], reversed_path[i + 1]):
                    return False

        return super()._valid_ann(ann, from_rel)  # type: ignore

    def _downstream_check(self, ann: "Ann", from_rel: Relationships) -> bool:
        """ASPA downstream check"""
        # downstream check
        if len(ann.as_path) <= 2:
            return super()._valid_ann(ann, from_rel)
        else:
            u_min = self._calculate_u_min(ann)  # type: ignore
            v_max_complement = self._calculate_v_max_complement(ann)

            v_max = len(ann.as_path) - v_max_complement
            if u_min <= v_max:
                return False
            else:
                return super()._valid_ann(ann, from_rel)

    def _calculate_u_min(self, ann: "Ann") -> int:
        """Calculates u_min from ASPA RFC"""

        path = ann.as_path
        # https://datatracker.ietf.org/doc/html/draft-ietf-sidrops-aspa-verification-16
        u_min = len(path) + 1  # type: ignore
        reversed_path = path[::-1]
        # For every adopting ASPA AS in the path,
        # The next ASN in the path must be in their providers list
        for i in range(len(reversed_path) - 1):
            if not self._provider_check(reversed_path[i], reversed_path[i + 1]):
                u_min = i + 2
                break

        return u_min

    def _calculate_v_max_complement(self, ann: "Ann") -> int:
        """Calculates v_max_complement from ASPA RFC"""

        v_max_complement = 0
        for i in range(len(ann.as_path) - 1):
            if not self._provider_check(ann.as_path[i], ann.as_path[i + 1]):
                v_max_complement = i + 1
                break
        return v_max_complement

    def _provider_check(self, asn1: int, asn2: int) -> bool:
        """Returns False if asn2 is not in asn1's provider_asns, AND asn1 adopts ASPA"""

        cur_as_obj = self.as_.as_graph.as_dict[asn1]
        if isinstance(cur_as_obj.policy, ASPA):
            next_as_obj = self.as_.as_graph.as_dict[asn2]
            if next_as_obj.asn not in cur_as_obj.provider_asns:
                return False
        return True
