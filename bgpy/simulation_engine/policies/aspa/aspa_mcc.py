from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships

from .aspapp import ASPAPP

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann



class ASPA_MCC(ASPAPP):
    """
    ASPA++ using only the max customer chain (mcc) checks.
    Cases 1 and 2 are skipped entirely since they only check mpc.
    Case 3 only applies the mcc bounds (hops toward origin and toward F),
    skipping the mpc bounds.
    """
    name = "ASPA-MCC"

    def _aspapp_valid(self, ann: "Ann", from_rel: Relationships) -> bool:
        as_dict = self.as_.as_graph.as_dict
        rpath = ann.as_path[::-1]
        n = len(rpath) - 1

        if from_rel == Relationships.CUSTOMERS:
            # mcc has no information about purely upward paths
            return True

        elif from_rel == Relationships.PEERS:
            # mcc has no information about purely upward paths
            return True

        elif from_rel == Relationships.PROVIDERS:
            return self._provider_valid(rpath, n, as_dict)

        else:
            raise NotImplementedError("Relationship not accounted for")

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
            if obj is None or not isinstance(obj.policy, ASPA_MCC):
                continue
            mcc = obj.max_customer_depth

            if i <= k0:
                # Upward segment: hops below p_i toward origin
                if mcc is not None and i - self.DOWN_SLACK > mcc:
                    return False

            elif i > k1:
                # Downward segment: hops below p_i toward F
                if mcc is not None and (n - i + 1) - self.DOWN_SLACK > mcc:
                    return False

        return True