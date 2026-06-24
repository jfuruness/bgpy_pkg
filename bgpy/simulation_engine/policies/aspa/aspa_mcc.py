from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships

from .aspapp import ASPAPP

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann



class ASPA_MCC(ASPAPP):
    name = "ASPA-MCC"

    def _aspapp_valid(self, ann: "Ann", from_rel: Relationships) -> bool:
        as_dict = self.as_.as_graph.as_dict
        rpath = ann.as_path[::-1]
        n = len(rpath) - 1

        # Case 1: Received from customer
        # i - slack <= mcc_i
        if from_rel == Relationships.CUSTOMERS:
            for i, asn in enumerate(rpath):
                obj = as_dict.get(asn)
                if (obj is not None and isinstance(obj.policy, ASPAPP)
                        and obj.max_customer_depth is not None
                        and i - self.DOWN_SLACK > obj.max_customer_depth):
                    return False
                
            f_obj = self.as_
            if (f_obj.max_customer_depth is not None
                    and n + 1 - self.DOWN_SLACK > f_obj.max_customer_depth):
                return False
            return True

        # Case 2: Received from peer
        # i - slack <= mcc_i
        elif from_rel == Relationships.PEERS:
            for i, asn in enumerate(rpath):
                obj = as_dict.get(asn)
                if (obj is not None and isinstance(obj.policy, ASPAPP)
                        and obj.max_customer_depth is not None
                        and i - self.DOWN_SLACK > obj.max_customer_depth):
                    return False
            return True

        # Case 3: Received from provider
        elif from_rel == Relationships.PROVIDERS:
            path_asns = set(rpath)

            peak = self._find_peak(rpath, n, as_dict, path_asns)
            if peak is not None:
                return self._check_peak(rpath, n, as_dict, peak[0], peak[1])

            potential = self._potential_peaks(rpath, n, as_dict, path_asns)
            if not potential:
                return True
            for k0, k1 in potential:
                if self._check_peak(rpath, n, as_dict, k0, k1):
                    return True
            return False

        else:
            raise NotImplementedError("No Relationship? ( ͡• _•)")

    def _check_peak(
        self,
        rpath: tuple,
        n: int,
        as_dict: dict,
        k0: int,
        k1: int,
    ) -> bool:
        for i, asn in enumerate(rpath):
            obj = as_dict.get(asn)
            if obj is None or not isinstance(obj.policy, ASPAPP):
                continue
            mcc = obj.max_customer_depth

            if i <= k0:
                if mcc is not None and (i - self.DOWN_SLACK) > mcc:
                    return False

            if i >= k1:
                if mcc is not None and (n - i + 1 - self.DOWN_SLACK) > mcc:
                    return False

        return True