from typing import TYPE_CHECKING

from .ann_container import AnnContainer

if TYPE_CHECKING:
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

        prefix = ann.prefix
        dct = self.data
        list_of_anns = dct.get(prefix)
        if list_of_anns:
            list_of_anns.append(ann)
        else:
            dct[prefix] = [ann]

        # This implementation is much slower
        # self.data[ann.prefix] = self.data.get(ann.prefix, list()) + [ann]

    def get_ann_list(self, prefix: str) -> list["Ann"]:
        """Returns recevied ann list for a given prefix"""

        return self.data.get(prefix, list())
