from collections import defaultdict
from dataclasses import dataclass

from .. import bgp_as# import BGPAS
from ...announcement import Announcement

@dataclass
class SendInfo:
    withdrawal_ann: Announcement = None
    ann: Announcement = None

    @property
    def anns(self):
        return [x for x in [self.withdrawal_ann, self.ann]
                if x is not None]

    def __str__(self):
        return f"send_info: ann: {self.ann}, withdrawal_ann {self.withdrawal_ann}"


class SendQueue:
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement_list}
    """

    __slots__ = ["_info"]

    def __init__(self):
        self._info = defaultdict(lambda: defaultdict(SendInfo))

    def add_ann(self, neighbor_asn, ann):
        assert isinstance(neighbor_asn, int)
        assert isinstance(ann, Announcement)


        # Withdraw
        if ann.withdraw:
            send_info = self._info[neighbor_asn][ann.prefix]
            assert send_info.withdrawal_ann is None, f"replacing withdrawal? {send_info.withdrawal_ann}"
            if send_info.ann is not None and send_info.ann.prefix_path_attributes_eq(ann):
                del self._info[neighbor_asn][ann.prefix]
            else:
                send_info.withdrawal_ann = ann
        # Normal ann
        else:
            send_info = self._info[neighbor_asn][ann.prefix]
            assert send_info.ann is None, "Replacing valid ann?"
            err = "Can't send identical withdrawal and ann"
            err += f" {ann}, {send_info.withdrawal_ann}"
            assert not ann.prefix_path_attributes_eq(send_info.withdrawal_ann), err
            self._info[neighbor_asn][ann.prefix].ann = ann

    def get_send_info(self, neighbor_obj, prefix):
        neighbor_info = self._info.get(neighbor_obj.asn)
        if neighbor_info is None:
            return neighbor_info
        else:
            return neighbor_info.get(prefix)

    def info(self, neighbors):
        for neighbor_obj in neighbors:
            assert isinstance(neighbor_obj, bgp_as.BGPAS)
            for prefix, send_info in self._info[neighbor_obj.asn].items():
                for ann in send_info.anns:
                    yield neighbor_obj, prefix, ann

    def reset_neighbor(self, neighbor_asn):
        self._info.pop(neighbor_asn, None)
