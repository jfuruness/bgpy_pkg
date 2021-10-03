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
        return [x for x in [self.ann, self.withdrawal_ann]
                if x is not None]


class SendQueue:
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement_list}
    """

    __slots__ = ["_info"]

    def __init__(self):
        self._info = defaultdict(lambda: defaultdict(SendInfo))

    def add_ann(self, neighbor_asn, ann, prefix=None):
        assert isinstance(neighbor_asn, int)
        assert isinstance(ann, Announcement)
        assert prefix is None or isinstance(prefix, str)

        prefix = prefix if prefix is not None else ann.prefix

        # Withdraw
        if ann.withdraw:
            send_info = self._info[neighbor_asn][prefix]
            if send_info.ann is not None and send_info.ann.prefix_path_attributes_eq(ann):
                del self._info[neighbor_asn][prefix]
            else:
                send_info.withdrawal_ann = ann
        # Normal ann
        else:
            self._info[neighbor_asn][prefix].ann = ann

    def neighbor_prefix_anns(self, neighbors):
        for neighbor_obj in neighbors:
            assert isinstance(neighbor_obj, bgp_as.BGPAS)
            for prefix, send_info in self._info[neighbor_obj.asn].items():
                for ann in send_info.anns:
                    yield neighbor_obj, prefix, ann

    def reset_neighbor(self, neighbor_asn):
        self._info.pop(neighbor_asn, None)
