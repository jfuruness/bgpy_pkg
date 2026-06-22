from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships
from bgpy.simulation_engine import ASPA, ASRA

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ASPAPP(ASRA):
    name = "ASPA++"

    UP_SLACK: int = 0
    DOWN_SLACK: int = 0

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:
        if not super()._valid_ann(ann, from_rel):
            return False
        return self._aspapp_valid(ann, from_rel)

    def _aspapp_valid(self, ann: "Ann", from_rel: Relationships) -> bool:
        as_dict = self.as_.as_graph.as_dict
        rpath = ann.as_path[::-1]
        n = len(rpath) - 1  # index of last AS before F

        if from_rel == Relationships.CUSTOMERS:
            # n - i + 1 - slack <= mpc_i
            # (n - i + 1 = len(rpath) - i in code since n = len(rpath) - 1)
            for i, asn in enumerate(rpath):
                obj = as_dict.get(asn)
                if (obj is not None
                        and isinstance(obj.policy, ASPAPP)
                        and obj.max_provider_depth is not None
                        and len(rpath) - i - self.UP_SLACK > obj.max_provider_depth):
                    return False
            return True

        elif from_rel == Relationships.PEERS:
            # n - i - slack <= mpc_i
            # p_n and F are peers so the hop to F does not count
            for i, asn in enumerate(rpath):
                obj = as_dict.get(asn)
                if (obj is not None
                        and isinstance(obj.policy, ASPAPP)
                        and obj.max_provider_depth is not None
                        and len(rpath) - i - 1 - self.UP_SLACK > obj.max_provider_depth):
                    return False
            return True

        elif from_rel == Relationships.PROVIDERS:
            return self._provider_valid(rpath, n, as_dict)

        else:
            raise NotImplementedError("Relationship not accounted for")

    def _provider_valid(self, rpath: tuple, n: int, as_dict: dict) -> bool:
        path_asns = set(rpath)

        # Try to find exact peak — if found, apply tight bounds
        peak = self._find_peak(rpath, n, as_dict, path_asns)
        if peak is not None:
            return self._check_peak(rpath, n, as_dict, peak[0], peak[1])

        # Peak unknown — collect candidate peaks and accept if any passes
        candidates = self._candidate_peaks(rpath, n, as_dict, path_asns)
        if not candidates:
            return True  # no information to reject on, allow conservatively
        for k0, k1 in candidates:
            if self._check_peak(rpath, n, as_dict, k0, k1):
                return True
        return False  # no candidate peak is consistent with mpc/mcc values

    def _find_peak(
        self,
        rpath: tuple,
        n: int,
        as_dict: dict,
        path_asns: set,
    ) -> tuple[int, int] | None:
        """
        Attempt to identify the exact peak using:
        1. Two top ASes (Tier-1 or ASPA with no path neighbors as providers)
        2. ASRA confirmed peer link
        3. ASPA/ASRA confirmed shared provider
        Returns (k0, k1) where k0 is leftmost peak AS and k1 is rightmost,
        or None if the peak cannot be determined.
        """
        # 1. Two top ASes — bilateral peer peak
        top = self._top_indices(rpath, as_dict, path_asns)
        if len(top) >= 2:
            return (top[0], top[-1])

        # 2. ASRA confirmed peer link — bilateral peer peak
        for i in range(n):
            la = as_dict.get(rpath[i])
            ra = as_dict.get(rpath[i + 1])
            if (
                (la is not None and isinstance(la.policy, ASRA)
                 and rpath[i + 1] in la.peer_asns)
                or
                (ra is not None and isinstance(ra.policy, ASRA)
                 and rpath[i] in ra.peer_asns)
            ):
                return (i, i + 1)

        # 3. ASPA/ASRA confirmed shared provider peak
        for i in range(n - 1):
            la = as_dict.get(rpath[i])
            ma = as_dict.get(rpath[i + 1])
            ra = as_dict.get(rpath[i + 2])
            left_up = (
                (la is not None and isinstance(la.policy, ASPA)
                 and rpath[i + 1] in la.provider_asns)
                or
                (ma is not None and isinstance(ma.policy, ASRA)
                 and rpath[i] in ma.customer_asns)
            )
            right_up = (
                (ra is not None and isinstance(ra.policy, ASPA)
                 and rpath[i + 1] in ra.provider_asns)
                or
                (ma is not None and isinstance(ma.policy, ASRA)
                 and rpath[i + 2] in ma.customer_asns)
            )
            if left_up and right_up:
                return (i + 1, i + 1)

        return None

    def _top_indices(
        self,
        rpath: tuple,
        as_dict: dict,
        path_asns: set,
    ) -> list[int]:
        """
        Returns indices of Tier-1 ASes or ASPA ASes whose provider set
        contains none of the other ASes in the path.
        """
        top = []
        for i, asn in enumerate(rpath):
            obj = as_dict.get(asn)
            if obj is None:
                continue
            if obj.input_clique:
                top.append(i)
            elif (isinstance(obj.policy, ASPA)
                  and len(obj.provider_asns & path_asns) == 0):
                top.append(i)
        return top

    def _candidate_peaks(
        self,
        rpath: tuple,
        n: int,
        as_dict: dict,
        path_asns: set,
    ) -> list[tuple[int, int]]:
        """
        Returns candidate (k0, k1) peak positions when exact peak is unknown.
        Uses one top AS (partial peak) if available, otherwise bounds the
        range using UP/DOWN links classified via ASPA/ASRA records.
        """
        top = self._top_indices(rpath, as_dict, path_asns)

        if len(top) == 1:
            # Partial peak: top AS is confirmed part of the peak.
            # Candidates are the top AS and its immediate neighbors.
            p = top[0]
            candidates = [(p, p)]  # shared provider at p
            if p > 0:
                candidates.append((p - 1, p))   # bilateral peer: left neighbor
            if p < n:
                candidates.append((p, p + 1))   # bilateral peer: right neighbor
            return candidates

        # No top ASes: classify links using ASPA/ASRA to bound peak range.
        # Rightmost UP link: peak k0 must be at AS index > rightmost_up_link
        # Leftmost DOWN link: for shared provider k0 <= leftmost_down_link,
        #                     for bilateral peer k0 < leftmost_down_link
        rightmost_up = -1  # link index; -1 means no UP link found
        leftmost_down = n  # link index; n means no DOWN link found

        for i in range(n):
            la = as_dict.get(rpath[i])
            ra = as_dict.get(rpath[i + 1])
            is_up = (
                (la is not None and isinstance(la.policy, ASPA)
                 and rpath[i + 1] in la.provider_asns)
                or
                (ra is not None and isinstance(ra.policy, ASRA)
                 and rpath[i] in ra.customer_asns)
            )
            is_down = (
                (ra is not None and isinstance(ra.policy, ASPA)
                 and rpath[i] in ra.provider_asns)
                or
                (la is not None and isinstance(la.policy, ASRA)
                 and rpath[i + 1] in la.customer_asns)
            )
            if is_up and not is_down:
                rightmost_up = i
            if is_down and not is_up and leftmost_down == n:
                leftmost_down = i

        peak_min = rightmost_up + 1          # 0 if no UP links
        shared_max = min(leftmost_down, n)   # peak AS = first DOWN link AS
        bilateral_max = min(leftmost_down - 1, n - 1)  # k1 = k0+1 <= leftmost_down

        candidates = []
        for k in range(peak_min, shared_max + 1):
            candidates.append((k, k))
        for k in range(peak_min, bilateral_max + 1):
            candidates.append((k, k + 1))
        return candidates

    def _check_peak(
        self,
        rpath: tuple,
        n: int,
        as_dict: dict,
        k0: int,
        k1: int,
    ) -> bool:
        """
        Apply tight per-side mpc/mcc bounds given peak at (k0, k1).
        k0 = leftmost peak AS index (origin side).
        k1 = rightmost peak AS index (F side).
        For shared provider: k0 == k1.
        For bilateral peer: k1 == k0 + 1.
        ASes at the peak itself (k0 <= i <= k1) are not checked.
        """
        for i, asn in enumerate(rpath):
            obj = as_dict.get(asn)
            if obj is None or not isinstance(obj.policy, ASPAPP):
                continue
            mpc = obj.max_provider_depth  # max provider chain
            mcc = obj.max_customer_depth  # max customer chain

            if i <= k0:
                # Upward segment: p_i is below or at the left peak AS.
                # Hops above p_i to peak: k0 - i <= mpc_i
                if mpc is not None and k0 - i - self.DOWN_SLACK > mpc:
                    return False
                # Hops below p_i toward origin: i <= mcc_i
                if mcc is not None and i - self.DOWN_SLACK > mcc:
                    return False

            elif i > k1:
                # Downward segment: p_i is below the right peak AS.
                # Hops below p_i toward F: n - i + 1 <= mcc_i
                if mcc is not None and (n - i + 1) - self.DOWN_SLACK > mcc:
                    return False
                # Hops above p_i to peak: i - k1 <= mpc_i
                if mpc is not None and (i - k1) - self.DOWN_SLACK > mpc:
                    return False

        return True


class ASPAPP1(ASPAPP):
    name = "ASPA++1"
    UP_SLACK: int = 1
    DOWN_SLACK: int = 1


class ASPAPP2(ASPAPP):
    name = "ASPA++2"
    UP_SLACK: int = 2
    DOWN_SLACK: int = 2