from .aspapp import ASPAPP



class ASPA_MPC(ASPAPP):
    """
    ASPA++ using only the max provider chain (mpc) checks.
    Cases 1 and 2 are unchanged since they are purely mpc-based.
    Case 3 only applies the mpc bounds (hops to peak from each side),
    skipping the mcc bounds.
    """
    name = "ASPA-MPC"

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
            if obj is None or not isinstance(obj.policy, ASPA_MPC):
                continue
            mpc = obj.max_provider_depth

            if i <= k0:
                # Upward segment: hops above p_i to peak
                if mpc is not None and k0 - i - self.DOWN_SLACK > mpc:
                    return False

            elif i > k1:
                # Downward segment: hops above p_i to peak
                if mpc is not None and (i - k1) - self.DOWN_SLACK > mpc:
                    return False

        return True

