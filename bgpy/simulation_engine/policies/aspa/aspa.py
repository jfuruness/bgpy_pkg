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
            v_max = self._calculate_v_max(ann)

            if u_min <= v_max:
                return False
            else:
                # NOTE: everything past step 4 in the RFC does not result
                # in "invalid", so we omit them
                return super()._valid_ann(ann, from_rel)

    def _calculate_u_min(self, ann: "Ann") -> int:
        """Calculates u_min from ASPA RFC"""

        path = ann.as_path

        N = len(path)

        def convert_u_to_index(u: int) -> int:
            """Converts u to index in array

            For example, take AS path 1, 2, 666, 777
            In the ASPA RFC, this is  N, 3, 2,   1 indexed
            And in Python, this is    0, 1, 2,   3 indexed
            So to go from u to python index, you do:
            """
            return N - u

        # https://datatracker.ietf.org/doc/html/draft-ietf-sidrops-aspa-verification-16
        u_min = len(path) + 1  # type: ignore
        for u in range(2, N + 1):
            u_minus_one_index = convert_u_to_index(u - 1)
            u_index = convert_u_to_index(u)
            # False from this func is the same as "Not Provider+" from the ASPA RFC
            if not self._provider_check(path[u_minus_one_index], path[u_index]):
                u_min = u
                break
        return u_min

    def _calculate_v_max(self, ann: "Ann") -> int:
        """Calculates v_max from ASPA RFC"""

        N = len(ann.as_path)

        def convert_v_to_index(v: int) -> int:
            """Converts v to index in array

            For example, take AS path 1, 2, 666, 777
            In the ASPA RFC, this is  N, 3, 2,   1 indexed
            And in Python, this is    0, 1, 2,   3 indexed
            So to go from v to python index, you do:
            """
            return N - v

        v_max = 0
        for v in range(N - 1, 1 - 1, -1):
            v_index = convert_v_to_index(v)
            v_plus_one_index = convert_v_to_index(v + 1)
            # The provider check returning false is the same as the hop func
            # described in the ASPA RFC section 5 returning "Not Provider+"
            if not self._provider_check(
                ann.as_path[v_plus_one_index], ann.as_path[v_index]
            ):
                v_max = v
                break
        return v_max

    def _provider_check(self, asn1: int, asn2: int) -> bool:
        """Returns False if asn2 is not in asn1's provider_asns, AND asn1 adopts ASPAi

        This also essentially can take the place of the "hop check" listed in
        ASPA RFC section 5
        """

        cur_as_obj = self.as_.as_graph.as_dict[asn1]
        if isinstance(cur_as_obj.policy, ASPA):
            next_as_obj = self.as_.as_graph.as_dict[asn2]
            if next_as_obj.asn not in cur_as_obj.provider_asns:
                return False
        return True
