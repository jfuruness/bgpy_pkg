from .aspapp import ASPAPP



class ASPA_MPC(ASPAPP):
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
                if mpc is not None and k0 - i - self.UP_SLACK <= mpc:
                    return False

            elif i > k1:
                if mpc is not None and i - k1 - self.UP_SLACK <= mpc:
                    return False

        return True