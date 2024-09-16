from typing import TYPE_CHECKING

from .ann_container import AnnContainer

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class LocalRIB(AnnContainer[str, "Ann"]):
    """Local RIB for a BGP AS"""

    def add_ann(self, ann: "Ann"):
        """Adds an announcement to local rib with prefix as key"""

        self.data[ann.prefix] = ann
