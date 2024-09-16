from typing import TYPE_CHECKING

from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine import Announcement as Ann


class EnforceFirstAS(BGP):
    """Deploys Enforce-First-AS

    On most routers this checks that the first ASN in the AS-Path is a neighbor
    This is used in ASPA based on the ASPA RFC
    """

    name: str = "Enforce-First-AS"

    def _valid_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """Returns False if first ASN is not a neighbor, else True"""

        # Note: This first if check has to be removed if you want to implement
        # route server to RS-Client behaviour
        if self._enforce_first_as_valid(ann, from_rel):
            return super()._valid_ann(ann, from_rel)
        else:
            return False

    def _enforce_first_as_valid(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """Ensures the first ASN in the AS-Path is a neighbor

        NOTE: normally this would check for an exact match, but since we don't
        store which ASN the announcement came from anywhere, we just check if it
        is a neighbor to simulate
        """

        return (
            ann.next_hop_asn == ann.as_path[0]
            # Super janky, TODO
            and ann.next_hop_asn
            in getattr(self.as_, f"{from_rel.name.lower()[:-1]}_asns")
        )
