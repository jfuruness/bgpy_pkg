from typing import TYPE_CHECKING

from bgpy.shared.aspa_records import ASRACLPRecord, ASRACRecord, ASRALPRecord
from bgpy.shared.enums import Relationships

from .aspa import ASPA
from .asra_b_clp import ASRA_B_CLP

if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement as Ann


class ASRA_B_SCL(ASRA_B_CLP):
    """
    ASRA B utilizing customers and lateral-peers are published
    in separate records.
    """

    name = "ASRA_B_SCL"

    publishes_asra_record_types = (ASRACLPRecord, ASRACRecord, ASRALPRecord)

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

        # The peak can be anywhere from min_up_ramp to max_up_ramp - 1, since
        # ASes without an ASPA record leave the top of the up ramp uncertain
        max_up_ramp = self._get_max_up_ramp_length(ann)

        # Iterate from min_up_ramp to the end of the path, checking for fake links
        for i in range(min_up_ramp, n - 1):
            is_peak = min_up_ramp <= i < max_up_ramp
            if self._is_fake_link_cps(path[i], path[i + 1], is_peak=is_peak):
                return False
        return True

    def _is_fake_link_cps(self, asn1: int, asn2: int, is_peak: bool) -> bool:
        """Fake-link check with customer/peer separation.

        At the peak a customer or peer link can be valid,
        but in the down ramp only customer link is valid
        """

        aspa_record = self.aspa_records.get(asn1)
        if aspa_record is None or asn2 in aspa_record.provider_asns:
            return False

        asra_c_record = self.asra_c_records.get(asn1)
        asra_lp_record = self.asra_lp_records.get(asn1)
        asra_clp_record = self.asra_clp_records.get(asn1)

        if is_peak:
            if asra_c_record is not None and asra_lp_record is not None:
                valid_set = asra_c_record.customer_asns | asra_lp_record.peer_asns
            elif asra_clp_record is not None:
                valid_set = asra_clp_record.customer_and_peer_asns
            else:
                return False
        else:
            if asra_c_record is not None:
                valid_set = asra_c_record.customer_asns
            elif asra_clp_record is not None:
                valid_set = asra_clp_record.customer_and_peer_asns
            else:
                return False

        return asn2 not in valid_set