from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships
from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class PeerlockLite(BGP):
    """A policy that does PeerlockLite"""

    name: str = "Peerlock Lite"

    def _valid_ann(self, ann: "Ann", recv_rel: "Relationships") -> bool:
        """Returns announcement validity

        Returns false if there are ASes between input clique,
        otherwise uses standard ROV and BGP checks
        to determine validity
        """

        if self.valid_by_peerlock_lite(ann, recv_rel):
            # Use standard BGP to determine if the announcement is valid
            return super()._valid_ann(ann, recv_rel)
        # Invalid by peerlock lite
        else:
            return False

    def valid_by_peerlock_lite(self, ann: "Ann", recv_rel: "Relationships") -> bool:
        """Returns if tier-1 ASes are split by other ASNs that are not t1"""

        as_dict = self.as_.as_graph.as_dict
        if recv_rel == Relationships.CUSTOMERS:
            # Input clique has no providers, so if they are your customer,
            # there is a route leakage
            for asn in ann.as_path:
                if as_dict[asn].input_clique:
                    return False
        return True
