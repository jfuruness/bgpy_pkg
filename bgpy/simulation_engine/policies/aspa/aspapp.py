from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships
from bgpy.simulation_engine import ASRA_B_CLP

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ASPAPP(ASRA_B_CLP):
    name = "ASPA++"

    @property
    def UP_SLACK(self) -> int:
        return 0

    @property
    def DOWN_SLACK(self) -> int:
        return 0

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:
        # run ASPA + ASRA first
        if not super()._valid_ann(ann, from_rel):
            return False
        return self._aspapp_valid(ann, from_rel)

    def _aspapp_valid(self, ann: "Ann", from_rel: Relationships) -> bool:
        as_dict = self.as_.as_graph.as_dict
        rpath = ann.as_path[::-1]
        # print(rpath, flush=True)
        n = len(rpath) - 1  # index of last AS before F

        # Case 1: Received from customer
        # n - i + 1 - up_slack <= mpc_i
        # i - down_slack <= mcc_i
        if from_rel == Relationships.CUSTOMERS:
            for i, asn in enumerate(rpath):
                aspapp_record = self.aspapp_records.get(asn)
                if (aspapp_record is not None
                    and ((aspapp_record.max_provider_path is not None and n - i + 1 - self.UP_SLACK > aspapp_record.max_provider_path)
                    or (aspapp_record.max_customer_path is not None and i - self.DOWN_SLACK > aspapp_record.max_customer_path))
                ):
                    return False

            f_obj = self.as_
            if (f_obj.max_customer_depth is not None
                and n + 1 - self.DOWN_SLACK > f_obj.max_customer_depth):
                return False

            return True

        # Case 2: Received from peer
        # n - i - slack <= mpc_i
        # i - down_slack <= mcc_i
        elif from_rel == Relationships.PEERS:
            for i, asn in enumerate(rpath):
                aspapp_record = self.aspapp_records.get(asn)
                if (aspapp_record is not None
                    and ((aspapp_record.max_provider_path is not None and n - i - self.UP_SLACK > aspapp_record.max_provider_path)
                    or (aspapp_record.max_customer_path is not None and i - self.DOWN_SLACK > aspapp_record.max_customer_path))
                ):
                    return False
            return True

        # Case 3: Received from provider
        elif from_rel == Relationships.PROVIDERS:
            path_asns = set(rpath)

            # (1) try to find exact peak
            peak = self._find_peak(rpath, n, as_dict, path_asns)
            if peak is not None:
                return self._check_peak(rpath, n, as_dict, peak[0], peak[1])

            # (2) Peak unknown, collect potential peaks and accept if any pass
            potential = self._potential_peaks(rpath, n, as_dict, path_asns)
            if not potential:
                return True
            for k0, k1 in potential:
                if self._check_peak(rpath, n, as_dict, k0, k1):
                    return True
            return False

        else:
            raise NotImplementedError("No Relationship? ( ͡• _•)")

    def _find_peak(
        self,
        rpath: tuple,
        n: int,
        as_dict: dict,
        path_asns: set,
    ) -> tuple[int, int] | None:
        """
        Attempt to identify the peak using:
            1. Two top ASes (Tier-1 or ASPA with no path neighbors as providers)
            2. ASRA confirmed peer link
            3. ASPA/ASRA confirmed shared provider
        Returns (k0, k1) where k0 is leftmost peak AS and k1 is rightmost
        or None if the peak cannot be determined.
        """
        # (1) Two top ASes = bilateral peer peak
        top = self._top_indices(rpath, as_dict, path_asns)
        if len(top) >= 2:
            return (top[0], top[-1])

        # (2) ASRA confirmed peer link = bilateral peer peak
        for i in range(n):
            la = self.asra_lp_records.get(rpath[i])
            ra = self.asra_lp_records.get(rpath[i + 1])
            if (
                (la is not None and rpath[i + 1] in la.peer_asns)
                or
                (ra is not None and rpath[i] in ra.peer_asns)
            ):
                return (i, i + 1)

        # (3) ASPA/ASRA confirmed shared provider peak
        for i in range(n - 1):
            la_aspa = self.aspa_records.get(rpath[i])
            ma_asra_c = self.asra_c_records.get(rpath[i+1])
            ra_aspa = self.aspa_records.get(rpath[i+2])
            left_up = (
                (la_aspa is not None and rpath[i + 1] in la_aspa.provider_asns)
                or
                (ma_asra_c is not None and rpath[i] in ma_asra_c.customer_asns)
            )
            right_up = (
                (ra_aspa is not None and rpath[i + 1] in ra_aspa.provider_asns)
                or
                (ma_asra_c is not None and rpath[i + 2] in ma_asra_c.customer_asns)
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
        contains none of the neighboring ASes in the path.
        """
        top = []
        for i, asn in enumerate(rpath):
            obj = as_dict.get(asn)
            if obj is None:
                continue
            if obj.input_clique:
                top.append(i)
            else:
                aspa_record = self.aspa_records.get(asn)
                if aspa_record is not None and len(aspa_record.provider_asns & path_asns) == 0:
                    top.append(i)
        return top

    def _potential_peaks(
        self,
        rpath: tuple,
        n: int,
        as_dict: dict,
        path_asns: set,
    ) -> list[tuple[int, int]]:
        """
        Returns potential peak positions (k0, k1) when exact peak is unknown.
        Uses one top AS (partial peak) if available, otherwise bounds the
        range using UP/DOWN links classified via ASPA/ASRA records.
        """
        top = self._top_indices(rpath, as_dict, path_asns)

        if len(top) == 1:
            # Partial peak: top AS is confirmed part of the peak
            # Immediate neighbors are potential a part of the peak
            p = top[0]
            potential_peaks = [(p, p)]

            if p > 0:
                la_aspa = self.aspa_records.get(rpath[p - 1])
                ra_aspa = self.aspa_records.get(rpath[p])
                la_asra_c = self.asra_c_records.get(rpath[p - 1])
                ra_asra_c = self.asra_c_records.get(rpath[p])
                # Only add (p-1, p) as bilateral peer if the link is not
                # already confirmed as UP or DOWN
                link_confirmed = (
                    (ra_aspa is not None and rpath[p - 1] in ra_aspa.provider_asns)
                    or
                    (la_asra_c is not None and rpath[p] in la_asra_c.customer_asns)
                    or
                    (la_aspa is not None and rpath[p] in la_aspa.provider_asns)
                    or
                    (ra_asra_c is not None and rpath[p - 1] in ra_asra_c.customer_asns)
                )
                if not link_confirmed:
                    potential_peaks.append((p - 1, p))

            if p < n:
                la_aspa = self.aspa_records.get(rpath[p])
                ra_aspa = self.aspa_records.get(rpath[p + 1])
                la_asra_c = self.asra_c_records.get(rpath[p])
                ra_asra_c = self.asra_c_records.get(rpath[p + 1])

                # Only add (p, p+1) as bilateral peer if the link is not
                # already confirmed as UP or DOWN
                link_confirmed = (
                    (ra_aspa is not None and rpath[p] in ra_aspa.provider_asns)
                    or
                    (la_asra_c is not None and rpath[p + 1] in la_asra_c.customer_asns)
                    or
                    (la_aspa is not None and rpath[p + 1] in la_aspa.provider_asns)
                    or
                    (ra_asra_c is not None and rpath[p] in ra_asra_c.customer_asns)
                )
                if not link_confirmed:
                    potential_peaks.append((p, p + 1))

            return potential_peaks

        # No top ASes, classify links using ASPA/ASRA to bound peak range
        rightmost_up = -1
        leftmost_down = n

        for i in range(n):
            la_aspa = self.aspa_records.get(rpath[i])
            ra_aspa = self.aspa_records.get(rpath[i + 1])
            la_asra_c = self.asra_c_records.get(rpath[i])
            ra_asra_c = self.asra_c_records.get(rpath[i + 1])

            is_up = (
                (la_aspa is not None and rpath[i + 1] in la_aspa.provider_asns)
                or
                (ra_asra_c is not None and rpath[i] in ra_asra_c.customer_asns)
            )
            is_down = (
                (ra_aspa is not None and rpath[i] in ra_aspa.provider_asns)
                or
                (la_asra_c is not None and rpath[i + 1] in la_asra_c.customer_asns)
            )
            if is_up and not is_down:
                rightmost_up = i
            if is_down and not is_up and leftmost_down == n:
                leftmost_down = i

        peak_min = rightmost_up + 1
        shared_max = min(leftmost_down, n)
        bilateral_max = min(leftmost_down - 1, n - 1)

        potential_peaks = []
        for k in range(peak_min, shared_max + 1):
            potential_peaks.append((k, k))
        for k in range(peak_min, bilateral_max + 1):
            potential_peaks.append((k, k + 1))
        return potential_peaks

    def _check_peak(
        self,
        rpath: tuple,
        n: int,
        as_dict: dict,
        k0: int,
        k1: int,
    ) -> bool:
        """
        Peak
        """
        for i, asn in enumerate(rpath):
            aspapp_record = self.aspapp_records.get(asn)
            if aspapp_record is None:
                continue
            mpc = aspapp_record.max_provider_path
            mcc = aspapp_record.max_customer_path

            if i <= k0:
                if mpc is not None and (k0 - i - self.UP_SLACK) > mpc:
                    return False
                if mcc is not None and (i - self.DOWN_SLACK) > mcc:
                    return False

            if i >= k1:
                if mpc is not None and (i - k1 - self.UP_SLACK) > mpc:
                    return False
                if mcc is not None and (n - i + 1 - self.DOWN_SLACK) > mcc:
                    return False

        f_obj = self.as_
        if (f_obj.max_provider_depth is not None
            and (n + 1 - k1 - self.DOWN_SLACK) > f_obj.max_provider_depth):
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
