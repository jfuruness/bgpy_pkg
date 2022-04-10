from typing import Optional

from .ann_container import AnnContainer

from ...announcements import Announcement as Ann


class RIBsOut(AnnContainer):
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement}
    """

    __slots__ = ()

    def get_ann(self, neighbor_asn: int, prefix: str) -> Optional[Ann]:
        """Returns Ann for a given neighbor asn and prefix"""

        if neighbor_asn in self._info:
            return self._info[neighbor_asn].get(prefix)
        else:
            self._info[neighbor_asn] = dict()
            return None

    def add_ann(self, neighbor_asn: int, ann: Ann):
        """Adds announcement to the ribs out"""

        if neighbor_asn in self._info:
            self._info[neighbor_asn][ann.prefix] = ann
        else:
            self._info[neighbor_asn] = {ann.prefix: ann}

    def remove_entry(self, neighbor_asn: int, prefix: str):
        """Removes ann from ribs out"""

        if neighbor_asn in self._info:
            del self._info[neighbor_asn][prefix]

    def neighbors(self):
        """Return all neighbors from the ribs out"""

        return self._info.keys()
