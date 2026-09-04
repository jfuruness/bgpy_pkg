from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships

from .aspa import ASPA

if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement as Ann


class ASRA_B_CLP(ASPA):
    """Algorithm B using ASRA-CLP records"""

    name = "ASRA-B-CLP"

    publishes_asra_records: bool = True

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:
        """
        1) Perform standard ASPA route-leak detection via super().
           If super() returns False => 'Invalid'. We bail out.
        2) If super() returns True => route is either 'Valid' or 'Unknown'.
           If from_rel == PROVIDER, we run the extra ASRA-B check:
             - We figure out min_up_ramp
             - For each hop from min_up_ramp to the end of the path, check
               if it's a fake link.
           Otherwise, we do nothing more.
        """
        # 1) Run ASPA's logic
        aspa_result = super()._valid_ann(ann, from_rel)

        # If ASPA deems it invalid, bail
        if not aspa_result:
            return False

        # 2) If from_rel is not PROVIDER, do nothing more
        if from_rel != Relationships.PROVIDERS:
            return True

        # If from_rel == PROVIDER, do ASRA-B "fake link" checks
        # i.e., check from min_up_ramp up to the end of the path

        path = ann.as_path[::-1]
        n = len(path)

        # Compute min_up_ramp in a simple way:
        # We start from the origin side (index 0) going forward until
        # we find the first place the ASPA "provider check" fails.
        min_up_ramp = self._get_min_up_ramp_length(ann)

        # If min_up_ramp == n, that means every hop was "provider+",
        # so there's no leftover "down-ramp" region to apply ASRA to,
        # and the route remains valid or unknown => accept it
        if min_up_ramp == n:
            return True

        # Else, check each hop from i=min_up_ramp..(n-2),
        # i.e., the region from the top of the up-ramp to the second-last
        # AS in the path.  (We examine i -> i+1.)
        for i in range(min_up_ramp, n - 1):
            if self._is_fake_link(path[i], path[i + 1]):
                # RFC: "If Fake-Link(...) = Detected, then outcome => invalid"
                return False

        # If no fake link discovered, keep it
        return True

    def _get_min_up_ramp_length(self, ann: "Ann") -> int:
        """
        We define min_up_ramp ~ the first 'i' from the origin side
        where the ASPA check fails or the AS published no ASPA record.

        If we never fail, we return len(path).
        """
        path = ann.as_path[::-1]
        for i in range(len(path) - 1):
            asn1 = path[i]
            asn2 = path[i + 1]

            aspa_record = self.aspa_records.get(asn1)

            # If asn1 published no ASPA record we treat that as
            # 'No Attestation', so min_up_ramp ends here. This covers the case
            # where asn1 isn't in the graph at all
            if aspa_record is None:
                return i

            # If asn2 is not in asn1's published provider list => 'Not Provider+',
            # so min_up_ramp ends here
            if asn2 not in aspa_record.provider_asns:
                return i

        return len(path)

    def _is_fake_link(self, asn1: int, asn2: int) -> bool:
        """
        ASRA-B fake link check (Algorithm B).
        "If AS(i) has valid ASPA(s) and does not list AS(i+1) as a provider,
         AND AS(i) has valid ASRA(s) and does not list AS(i+1) as neighbor,
         => FAKE LINK."

        Both conditions key off published records rather than asn1's policy, so
        an AS can publish without verifying. A missing record means "no
        attestation", which is never a failure.

        This variant reads ASRA-CLP records, which merge customers and lateral
        peers into a single set.
        """

        aspa_record = self.aspa_records.get(asn1)
        asra_record = self.asra_clp_records.get(asn1)

        # A record asn1 never published attests nothing, so it can't detect
        # a fake link. Both records are required to declare one
        if aspa_record is None or asra_record is None:
            return False

        # 1) asn1's ASPA does NOT list asn2 as a provider, and
        # 2) asn1's ASRA-CLP does NOT list asn2 as a customer or lateral peer
        return (
            asn2 not in aspa_record.provider_asns
            and asn2 not in asra_record.customer_and_peer_asns
        )
