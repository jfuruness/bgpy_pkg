import dataclasses
from typing import TYPE_CHECKING, Iterator, Optional

from yamlable import YamlAble, yaml_info

from .ann_container import AnnContainer

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine import Announcement as Ann


@yaml_info(yaml_tag="AnnInfo")
@dataclasses.dataclass
class AnnInfo(YamlAble):
    """Dataclass for storing a ribs in Ann info

    These announcements are unprocessed, so we store
    the unprocessed_ann and also the recv_relationship
    (since the recv_relationship on the announcement is
    from the last AS and has not yet been updated)
    """

    unprocessed_ann: Optional["Ann"]
    recv_relationship: Optional["Relationships"]


class RIBsIn(AnnContainer[int, dict[str, AnnInfo]]):
    """Incomming announcements for a BGP AS

    neighbor: {prefix: (announcement, relationship)}
    """

    def get_unprocessed_ann_recv_rel(
        self, neighbor_asn: int, prefix: str
    ) -> AnnInfo | None:
        """Returns AnnInfo for a neighbor ASN and prefix

        We don't use defaultdict here because that's not yamlable
        """

        return self.data.get(neighbor_asn, dict()).get(prefix)

    def add_unprocessed_ann(
        self,
        unprocessed_ann: "Ann",
        recv_relationship: "Relationships",
    ):
        """Adds an unprocessed ann to ribs in

        We don't use default dict here because it's not yamlable
        """

        # Shorten the var name
        ann = unprocessed_ann
        if ann.as_path[0] not in self.data:
            self.data[ann.as_path[0]] = {
                ann.prefix: AnnInfo(
                    unprocessed_ann=unprocessed_ann, recv_relationship=recv_relationship
                )
            }
        else:
            self.data[ann.as_path[0]][ann.prefix] = AnnInfo(
                unprocessed_ann=unprocessed_ann, recv_relationship=recv_relationship
            )

    def get_ann_infos(self, prefix: str) -> Iterator[AnnInfo]:
        """Returns AnnInfos for a given prefix"""

        default_ann_info: AnnInfo = AnnInfo(
            unprocessed_ann=None, recv_relationship=None
        )
        for prefix_ann_info in self.data.values():
            yield prefix_ann_info.get(prefix, default_ann_info)

    def remove_entry(self, neighbor_asn: int, prefix: str):
        """Removes AnnInfo from RibsIn"""

        del self.data[neighbor_asn][prefix]
