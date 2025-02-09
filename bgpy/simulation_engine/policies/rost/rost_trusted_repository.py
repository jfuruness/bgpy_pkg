from collections import defaultdict

from bgpy.simulation_engine.announcement import Announcement as Ann


class RoSTTrustedRepository:
    def __init__(self) -> None:
        # {prefix: {id: active?}}
        # Since we don't do batches in sims, id is just asn
        self.info: defaultdict[str, dict[int, bool]] = defaultdict(dict)

    def __repr__(self) -> str:
        return str(self.info)

    def clear(self) -> None:
        self.__init__()  # type: ignore

    def add_ann(self, ann: Ann, asn: int, active: bool) -> None:
        self.info[ann.prefix][asn] = active

    def seen_withdrawal(self, ribs_in_ann: Ann) -> bool:
        rost_id_statuses_for_prefix = self.info[ribs_in_ann.prefix]
        for rost_id in ribs_in_ann.rost_ids:
            # This checks if it's active or not. Active=True
            if rost_id_statuses_for_prefix[rost_id] is False:
                return True
        return False
