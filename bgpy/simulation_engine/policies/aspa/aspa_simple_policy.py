from typing import TYPE_CHECKING

from bgpy.enums import Relationships
from bgpy.simulation_engine.policies.bgp import BGPSimplePolicy

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ASPASimplePolicy(BGPSimplePolicy):
    """An Policy that deploys ASPA"""

    name: str = "ASPASimple"

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:  # type: ignore
        """Returns False if from peer/customer when aspa is set"""

        assert len(set(ann.as_path)) == len(ann.as_path), "We deal with prepending"

        # If ann.aspa is set, only accept from a provider
        if from_rel.value in (Relationships.CUSTOMERS.value, Relationships.PEERS.value):
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
            reversed_as_path = list(reversed(ann.as_path))  # type: ignore
            # For every adopting ASPA AS in the path,
            # The next ASN in the path must be in their providers list
            for i, asn in enumerate(reversed_as_path):
                # This is the end of the AS Path
                if i == len(reversed_as_path) - 1:
                    break
                cur_as_obj = self.as_.as_graph.as_dict[asn]
                if isinstance(cur_as_obj.policy, ASPASimplePolicy):
                    next_as_obj = self.as_.as_graph.as_dict[reversed_as_path[i + 1]]
                    if next_as_obj.asn not in cur_as_obj.provider_asns:
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

        # https://datatracker.ietf.org/doc/html/draft-ietf-sidrops-aspa-verification-16
        u_min = len(ann.as_path) + 1  # type: ignore
        reversed_as_path = list(reversed(ann.as_path))
        # For every adopting ASPA AS in the path,
        # The next ASN in the path must be in their providers list
        for i, asn in enumerate(reversed_as_path):
            # This is the end of the AS Path
            if i == len(reversed_as_path) - 1:
                break
            cur_as_obj = self.as_.as_graph.as_dict[asn]
            if isinstance(cur_as_obj.policy, ASPASimplePolicy):
                next_as_obj = self.as_.as_graph.as_dict[reversed_as_path[i + 1]]
                if next_as_obj.asn not in cur_as_obj.provider_asns:
                    u_min = i + 2
                    break
        return u_min

    def _calculate_v_max_complement(self, ann: "Ann") -> int:
        """Calculates v_max_complement from ASPA RFC"""

        v_max_complement = 0
        for i, asn in enumerate(ann.as_path):
            # This is the end of the AS Path
            if i == len(ann.as_path) - 1:
                break
            cur_as_obj = self.as_.as_graph.as_dict[asn]
            if isinstance(cur_as_obj.policy, ASPASimplePolicy):
                next_as_obj = self.as_.as_graph.as_dict[ann.as_path[i + 1]]
                if next_as_obj.asn not in cur_as_obj.provider_asns:
                    v_max_complement = i + 2
                    break
        return v_max_complement
