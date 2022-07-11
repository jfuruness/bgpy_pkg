from .ann_container import AnnContainer

from ..announcement import Announcement


class RecvQueue(AnnContainer):
    """Adj_RIBs_In for a BGP AS

    Map prefixes to anns sent
    {prefix: list_of_ann}
    """

    __slots__ = ()

    def add_ann(self, ann: Announcement):
        """Appends ann to the list of recieved ann for that prefix

        We don't use defaultdict here because those are not yamlable
        """

        self._info[ann.prefix] = self._info.get(ann.prefix, list()) + [ann]

    def prefix_anns(self):
        """Returns all prefixes and announcement lists zipped"""

        return self._info.items()

    def get_ann_list(self, prefix):
        """Returns recevied ann list for a given prefix"""

        return self._info.get(prefix, [])
