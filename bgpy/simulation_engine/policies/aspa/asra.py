from typing import TYPE_CHECKING

from bgpy.enums import Relationships

from .aspa import ASPA

if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement as Ann


class ASRA(ASPA):
    """Algo B using ASRA records 3"""

    name = "ASRA"

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

        path = ann.as_path
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
        where the ASPA check fails or the AS does not adopt ASPA.

        If we never fail, we return len(path).
        """
        path = ann.as_path
        for i in range(len(path) - 1):
            asn1 = path[i]
            asn2 = path[i + 1]
            asn1_obj = self.as_.as_graph.as_dict[asn1]

            # If asn1 does not adopt ASPA, we treat that
            # as 'No Attestation', so min_up_ramp ends here.
            if not isinstance(asn1_obj.policy, ASPA):
                return i

            # If asn2 is not in asn1's provider list => 'Not Provider+',
            # so min_up_ramp ends here
            if asn2 not in asn1_obj.provider_asns:
                return i

        return len(path)

    def _is_fake_link(self, asn1: int, asn2: int) -> bool:
        """
        ASRA-B fake link check (Algorithm B).
        "If AS(i) has valid ASPA(s) and does not list AS(i+1) as a provider,
         AND AS(i) has valid ASRA(s) and does not list AS(i+1) as neighbor,
         => FAKE LINK."

        We'll interpret "valid ASPA(s)" as "this AS is adopting ASPA
        (i.e. policy is ASPA or child class), and asn2 is not in
        asn1.provider_asns."

        We'll interpret "valid ASRA(s)" as "this AS is adopting ASRA
        (i.e. policy is ASRA or child class), and asn2 is not in
        asn1.neighbor_asns."
        """
        asn1_obj = self.as_.as_graph.as_dict[asn1]

        # Must meet BOTH conditions to declare fake link:
        # 1) asn1 adopts ASPA and does NOT list asn2 as a provider
        has_aspa_but_not_provider = isinstance(asn1_obj.policy, ASPA) and (
            asn2 not in asn1_obj.provider_asns
        )

        # 2) asn1 also adopts ASRA and does NOT list asn2 as neighbor
        has_asra_but_not_neighbor = isinstance(asn1_obj.policy, ASRA) and (
            asn2 not in asn1_obj.neighbor_asns
        )

        # If both are True => fake link
        return has_aspa_but_not_provider and has_asra_but_not_neighbor
