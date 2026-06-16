from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships

from .aspa import ASPA
from .asra import ASRA

if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement as Ann

class ASRAPCS(ASRA):
    """
        ASRA with Customer/Peer Separation.
    """

    name = "ASRAPCS"

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:
        
        # Do ASPA Check
        if not ASPA._valid_ann(self, ann, from_rel):
            return False

        # We only care about announcements from providers
        if from_rel != Relationships.PROVIDERS:
            return True

        path = ann.as_path[::-1]
        n = len(path)
        min_up_ramp = self._get_min_up_ramp_length(ann)

        if min_up_ramp == n:
            return True

        # Iterate from min_up_ramp to the end of the path, checking for fake links
        for i in range(min_up_ramp, n - 1):
            if self._is_fake_link_cps(path[i], path[i + 1], is_peak=(i == min_up_ramp)):
                return False
        return True

    def _is_fake_link_cps(self, asn1: int, asn2: int, is_peak: bool) -> bool:
        """Fake-link check with customer/peer separation.

        At the peak a customer or peer link can be valid, 
        but in the down ramp only customer link is valid
        """

        asn1_obj = self.as_.as_graph.as_dict.get(asn1)
        if not asn1_obj:
            return False

        # ASN1 has ASPA but ASN2 is not its provider
        has_aspa_but_not_provider = (
            isinstance(asn1_obj.policy, ASPA)
            and asn2 not in asn1_obj.provider_asns
        )

        # Direction-specific check
        if isinstance(asn1_obj.policy, ASRAPCS):
            valid_set = (
                asn1_obj.customer_asns | asn1_obj.peer_asns
                if is_peak
                else asn1_obj.customer_asns
            )
            not_valid_direction = asn2 not in valid_set
        else:
            # Doesn't adopt ASRAPCS, fall back to basic neighbor check
            not_valid_direction = asn2 not in asn1_obj.neighbor_asns

        return has_aspa_but_not_provider and not_valid_direction
