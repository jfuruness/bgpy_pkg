from typing import ItemsView, Optional

from .ann_container import AnnContainer

from bgpy.simulation_engine import Announcement as Ann


class RecvQueue(AnnContainer[str, list["Ann"]]):
    """Adj_RIBs_In for a BGP AS

    Map prefixes to anns sent
    {prefix: list_of_ann}
    """

    def add_ann(self, ann: "Ann"):
        """Appends ann to the list of recieved ann for that prefix

        We don't use defaultdict here because those are not yamlable
        """

        self.data[ann.prefix] = self.data.get(ann.prefix, list()) + [ann]

    def prefix_anns(self) -> ItemsView[str, list["Ann"]]:
        """Returns all prefixes and announcement lists zipped"""

        return self.data.items()

    def get_ann_list(self, prefix: str) -> list["Ann"]:
        """Returns recevied ann list for a given prefix"""

        # mypy can't handle this, just ignore
        return self.data.get(prefix, list())  # type: ignore
