from typing import Dict, ItemsView, List, Optional

from .ann_container import AnnContainer
from ..announcement import Announcement as Ann


class RecvQueue(AnnContainer):
    """Adj_RIBs_In for a BGP AS

    Map prefixes to anns sent
    {prefix: list_of_ann}
    """

    __slots__ = ()

    def __init__(self, _info: Optional[Dict[str, List[Ann]]] = None):
        """Stores _info dict which contains recv_queue

        This is passed in so that we can regenerate this class from yaml

        Note that we do not use a defaultdict here because that is not
        yamlable using the yamlable library
        """

        self._info: Dict[str, List[Ann]] = _info if _info is not None else dict()

    def add_ann(self, ann: Ann):
        """Appends ann to the list of recieved ann for that prefix

        We don't use defaultdict here because those are not yamlable
        """

        self._info[ann.prefix] = self._info.get(ann.prefix, list()) + [ann]

    def prefix_anns(self) -> ItemsView[str, List[Ann]]:
        """Returns all prefixes and announcement lists zipped"""

        return self._info.items()

    def get_ann_list(self, prefix: str) -> List[Ann]:
        """Returns recevied ann list for a given prefix"""

        # mypy can't handle this, just ignore
        return self._info.get(prefix, list())  # type: ignore
