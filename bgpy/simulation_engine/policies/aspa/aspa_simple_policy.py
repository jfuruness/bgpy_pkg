from typing import TYPE_CHECKING

from bgpy.enums import Relationships
from bgpy.simulation_engine.policies.bgp import BGPSimplePolicy

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine import Announcement as Ann


class ASPASimplePolicy(BGPSimplePolicy):
    """An Policy that deploys ASPA"""

    name: str = "ASPASimple"

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:  # type: ignore
        """Returns False if from peer/customer when aspa is set"""

        assert len(set(ann.as_path)) == len(ann.as_path), "We deal with prepending"

        # If ann.aspa is set, only accept from a provider
        if from_rel.value in (Relationships.CUSTOMERS.value, Relationships.PEERS.value):
            # Upstream check
            if len(ann.as_path) == 1:
                return super()._valid_ann(ann, from_rel)
            else:
                reversed_as_path = list(reversed(ann.as_path))
                # For every adopting ASPA AS in the path,
                # The next ASN in the path must be in their providers list
                for i, asn in enumerate(reversed_as_path):
                    # This is the end of the AS Path
                    if i == len(reversed_as_path):
                        continue
                    cur_as_obj = self.as_.as_graph.as_dict[asn]
                    if isinstance(cur_as_obj.policy, ASPASimplePolicy):
                        next_as_obj = self.as_.as_graph.as_dict[reversed_as_path[i + 1]]
                        if next_as_obj not in cur_as_obj.providers:
                            return False
        elif from_rel.value == Relationships.PROVIDERS.value:
            # downstream check
            if len(ann.as_path) <= 2:
                return super()._valid_ann(ann, from_rel)
            else:
                # https://datatracker.ietf.org/doc/html/draft-ietf-sidrops-aspa-verification-16
                u_min = len(ann.as_path) + 1
                reversed_as_path = list(reversed(ann.as_path))
                # For every adopting ASPA AS in the path,
                # The next ASN in the path must be in their providers list
                for i, asn in enumerate(reversed_as_path):
                    # This is the end of the AS Path
                    if i == len(reversed_as_path) - 1:
                        continue
                    cur_as_obj = self.as_.as_graph.as_dict[asn]
                    if isinstance(cur_as_obj.policy, ASPASimplePolicy):
                        next_as_obj = self.as_.as_graph.as_dict[reversed_as_path[i + 1]]
                        if next_as_obj not in cur_as_obj.providers:
                            u_min = i + 2
                            break
                # V calculation
                v_max_complement = 0
                for i, asn in enumerate(ann.as_path):
                    # This is the end of the AS Path
                    if i == len(ann.as_path) - 1:
                        continue
                    cur_as_obj = self.as_.as_graph.as_dict[asn]
                    if isinstance(cur_as_obj.policy, ASPASimplePolicy):
                        next_as_obj = self.as_.as_graph.as_dict[ann.as_path[i + 1]]
                        if next_as_obj not in cur_as_obj.providers:
                            v_max_complement = i + 2
                            break

                v_max = len(ann.as_path) - v_max_complement
                if u_min <= v_max:
                    return False
                else:
                    return super()._valid_ann(ann, from_rel)
        else:
            raise NotImplementedError("Should never reach here")

        return super()._valid_ann(ann, from_rel)
