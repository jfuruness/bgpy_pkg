from collections import defaultdict
from dataclasses import dataclass
from typing import List, Optional

from lib_caida_collector import AS

from ...announcements import Announcement as Ann


@dataclass
class SendInfo:
    withdrawal_ann: Ann = None
    ann: Ann = None

    @property
    def anns(self):
        return [x for x in [self.withdrawal_ann, self.ann]
                if x is not None]

    def __str__(self):
        return f"send_info: ann: {self.ann}, withdrawal {self.withdrawal_ann}"


class SendQueue:
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement_list}
    """

    __slots__ = "_info",

    def __init__(self):
        self._info = defaultdict(lambda: defaultdict(SendInfo))

    def __eq__(self, other):
        # Remove this after updating the system tests
        if isinstance(other, dict):
            return self._info == other
        elif isinstance(other, SendQueue):
            return self._info == other._info
        else:
            raise NotImplementedError

    def add_ann(self, neighbor_asn: int, ann: Ann):

        # Withdraw
        if ann.withdraw:
            send_info = self._info[neighbor_asn][ann.prefix]
            msg = f"replacing withdrawal? {send_info.withdrawal_ann}"
            assert send_info.withdrawal_ann is None, msg
            if (send_info.ann is not None and
                    send_info.ann.prefix_path_attributes_eq(ann)):
                del self._info[neighbor_asn][ann.prefix]
            else:
                send_info.withdrawal_ann = ann
        # Normal ann
        else:
            send_info = self._info[neighbor_asn][ann.prefix]
            assert send_info.ann is None, "Replacing valid ann?"
            err = "Can't send identical withdrawal and ann"
            err += f" {ann}, {send_info.withdrawal_ann}"
            assert not ann.prefix_path_attributes_eq(
                send_info.withdrawal_ann), err
            self._info[neighbor_asn][ann.prefix].ann = ann

    def get_send_info(self, neighbor_obj: AS, prefix: str) -> Optional[Ann]:
        neighbor_info = self._info.get(neighbor_obj.asn)
        if neighbor_info is None:
            return neighbor_info
        else:
            return neighbor_info.get(prefix)

    def info(self, neighbors: List[AS]):
        for neighbor_obj in neighbors:
            # assert isinstance(neighbor_obj, bgp_as.BGPAS)
            for prefix, send_info in self._info[neighbor_obj.asn].items():
                for ann in send_info.anns:
                    yield neighbor_obj, prefix, ann

    def reset_neighbor(self, neighbor_asn: int):
        self._info.pop(neighbor_asn, None)
