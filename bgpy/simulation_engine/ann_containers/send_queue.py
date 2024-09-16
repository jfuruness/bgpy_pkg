from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterator

from yamlable import YamlAble, yaml_info

from bgpy.simulation_engine import Announcement as Ann

from .ann_container import AnnContainer

if TYPE_CHECKING:
    from bgpy.as_graphs import AS


@yaml_info(yaml_tag="SendInfo")
@dataclass
class SendInfo(YamlAble):
    withdrawal_ann: Ann | None = None
    ann: Ann | None = None

    @property
    def anns(self):
        return [x for x in [self.withdrawal_ann, self.ann] if x is not None]

    def __str__(self):
        return f"send_info: ann: {self.ann}, withdrawal {self.withdrawal_ann}"


class SendQueue(AnnContainer[int, dict[str, SendInfo]]):
    """Announcements to be sent for a BGP AS

    {neighbor: {prefix: SendInfo}}
    """

    def add_ann(self, neighbor_asn: int, ann: Ann):
        """Adds Ann to be sent"""

        # Used to be done by the defaultdict
        if neighbor_asn not in self.data:
            self.data[neighbor_asn] = {ann.prefix: SendInfo()}
        if ann.prefix not in self.data[neighbor_asn]:
            self.data[neighbor_asn][ann.prefix] = SendInfo()

        send_info = self.data[neighbor_asn][ann.prefix]

        # If the announcement is a withdraw
        if ann.withdraw:
            # Ensure withdrawls aren't replaced
            msg: str = f"replacing withdrawal? {send_info.withdrawal_ann}"
            assert send_info.withdrawal_ann is None, msg

            # If the withdrawal is equal to ann, delete both
            if send_info.ann is not None and send_info.ann.prefix_path_attributes_eq(
                ann
            ):
                del self.data[neighbor_asn][ann.prefix]
            # If withdrawl is not equal to Ann, add withdrawal
            else:
                send_info.withdrawal_ann = ann

        # If the announcement is not a withdrawal
        else:
            # Never replace valid Ann without a withdrawal
            assert send_info.ann is None, "Replacing valid ann?"
            err = "Can't send identical withdrawal and ann"
            err += f" {ann}, {send_info.withdrawal_ann}"
            assert not ann.prefix_path_attributes_eq(send_info.withdrawal_ann), err

            # Add announcement
            send_info.ann = ann

    def get_send_info(self, neighbor_obj: "AS", prefix: str) -> Ann | None:
        """Returns the SendInfo for a neighbor AS and prefix"""

        return self.data.get(neighbor_obj.asn, dict()).get(prefix)

    def info(self, neighbors: list["AS"]) -> Iterator[tuple["AS", str, Ann]]:
        """Returns neighbor obj, prefix, announcement"""

        for neighbor_obj in neighbors:
            # assert isinstance(neighbor_obj, bgp_as.BGPAS)
            for prefix, send_info in self.data.get(neighbor_obj.asn, dict()).items():
                for ann in send_info.anns:
                    yield neighbor_obj, prefix, ann
