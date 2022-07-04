from dataclasses import dataclass
from typing import List, Optional

from yamlable import YamlAble, yaml_info

from lib_caida_collector import AS


from .ann_container import AnnContainer

from ...announcement import Announcement as Ann


@yaml_info(yaml_tag="SendInfo")
@dataclass
class SendInfo(YamlAble):
    withdrawal_ann: Ann = None
    ann: Ann = None

    @property
    def anns(self):
        return [x for x in [self.withdrawal_ann, self.ann]
                if x is not None]

    def __str__(self):
        return f"send_info: ann: {self.ann}, withdrawal {self.withdrawal_ann}"


class SendQueue(AnnContainer):
    """Announcements to be sent for a BGP AS

    {neighbor: {prefix: SendInfo}}
    """

    __slots__ = ()

    def add_ann(self, neighbor_asn: int, ann: Ann):
        """Adds Ann to be sent"""

        # Used to be done by the defaultdict
        if neighbor_asn not in self._info:
            self._info[neighbor_asn] = {ann.prefix: SendInfo()}
        if ann.prefix not in self._info[neighbor_asn]:
            self._info[neighbor_asn][ann.prefix] = SendInfo()

        send_info = self._info[neighbor_asn][ann.prefix]

        # If the announcement is a withdraw
        if ann.withdraw:
            # Ensure withdrawls aren't replaced
            msg = f"replacing withdrawal? {send_info.withdrawal_ann}"
            assert send_info.withdrawal_ann is None, msg

            # If the withdrawal is equal to ann, delete both
            if (send_info.ann is not None and
                    send_info.ann.prefix_path_attributes_eq(ann)):
                del self._info[neighbor_asn][ann.prefix]
            # If withdrawl is not equal to Ann, add withdrawal
            else:
                send_info.withdrawal_ann = ann

        # If the announcement is not a withdrawal
        else:
            # Never replace valid Ann without a withdrawal
            assert send_info.ann is None, "Replacing valid ann?"
            err = "Can't send identical withdrawal and ann"
            err += f" {ann}, {send_info.withdrawal_ann}"
            assert not ann.prefix_path_attributes_eq(
                send_info.withdrawal_ann), err

            # Add announcement
            send_info.ann = ann

    def get_send_info(self, neighbor_obj: AS, prefix: str) -> Optional[Ann]:
        """Returns the SendInfo for a neighbor AS and prefix"""

        return self._info.get(neighbor_obj.asn, dict()).get(prefix)

    def info(self, neighbors: List[AS]):
        """Returns neighbor obj, prefix, announcement"""

        for neighbor_obj in neighbors:
            # assert isinstance(neighbor_obj, bgp_as.BGPAS)
            for prefix, send_info in self._info.get(neighbor_obj.asn,
                                                    dict()).items():
                for ann in send_info.anns:
                    yield neighbor_obj, prefix, ann

    def reset_neighbor(self, neighbor_asn: int):
        """Resets a neighbor, removing all send info"""

        self._info.pop(neighbor_asn, None)
