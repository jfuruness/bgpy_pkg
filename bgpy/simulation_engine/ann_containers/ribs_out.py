from typing import Iterable

from bgpy.simulation_engine import Announcement as Ann

from .ann_container import AnnContainer


class RIBsOut(AnnContainer[int, dict[str, Ann]]):
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement}
    """

    def get_ann(self, neighbor_asn: int, prefix: str) -> Ann | None:
        """Returns Ann for a given neighbor asn and prefix"""

        return self.data.get(neighbor_asn, dict()).get(prefix)

    def add_ann(self, neighbor_asn: int, ann: Ann) -> None:
        """Adds announcement to the ribs out"""

        if neighbor_asn in self.data:
            self.data[neighbor_asn][ann.prefix] = ann
        else:
            self.data[neighbor_asn] = {ann.prefix: ann}

    def remove_entry(self, neighbor_asn: int, prefix: str) -> None:
        """Removes ann from ribs out"""

        del self.data[neighbor_asn][prefix]

    def neighbors(self) -> Iterable[int]:
        """Return all neighbors from the ribs out"""

        return self.data.keys()
