from .aspapp import ASPAPP



class ASPA_MPC(ASPAPP):
    name = "ASPA-MPC"

    def _aspapp_valid(self, ann, from_rel):
        as_dict = self.as_.as_graph.as_dict
        rpath = ann.as_path[::-1]
        n = len(rpath) - 1

        if from_rel.CUSTOMERS:
            for i, asn in enumerate(rpath):
                obj = as_dict.get(asn)
                if (obj is not None and isinstance(obj.policy, ASPA_MPC)
                        and obj.max_provider_depth is not None
                        and n - i + 1 - self.UP_SLACK > obj.max_provider_depth):
                    return False
            return True

        elif from_rel.PEERS:
            for i, asn in enumerate(rpath):
                obj = as_dict.get(asn)
                if (obj is not None and isinstance(obj.policy, ASPA_MPC)
                        and obj.max_provider_depth is not None
                        and n - i - self.UP_SLACK > obj.max_provider_depth):
                    return False
            return True

        elif from_rel.PROVIDERS:
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
            if obj is None or not isinstance(obj.policy, ASPA_MPC):
                continue
            mpc = obj.max_provider_depth

            if i <= k0:
                if mpc is not None and (k0 - i - self.UP_SLACK) > mpc:
                    return False

            if i >= k1:
                if mpc is not None and (i - k1 - self.UP_SLACK) > mpc:
                    return False

        f_obj = self.as_
        if (f_obj.max_provider_depth is not None
                and (n + 1 - k1 - self.DOWN_SLACK) > f_obj.max_provider_depth):
            return False

        return True