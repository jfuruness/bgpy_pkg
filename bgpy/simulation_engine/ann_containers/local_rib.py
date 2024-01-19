from typing import Optional, TYPE_CHECKING

from .ann_container import AnnContainer


if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class LocalRIB(AnnContainer[str, "Ann"]):
    """Local RIB for a BGP AS"""

    def add_ann(self, ann: "Ann"):
        """Adds an announcement to local rib with prefix as key"""

        self.data[ann.prefix] = ann

    def remove_ann(self, prefix: str):
        """Removes announcement from local rib based on prefix"""

        del self.data[prefix]

    def prefix_anns(self):
        """Returns all prefixes and announcements zipped"""

        return self.data.items()

    def __str__(self) -> str:
        return str({k: str(v) for k, v in self.data.items()})
