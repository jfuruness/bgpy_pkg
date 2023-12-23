from typing import Iterator, Optional

from .ann_container import AnnContainer

from bgpy.simulation_engines.py_simulation_engine import PyAnnouncement as PyAnn
from bgpy.simulation_engines.cpp_simulation_engine import CPPAnnouncement as CPPAnn


class RIBsOut(AnnContainer):
    """Incomming announcements for a BGP AS

    neighbor: {prefix: announcement}
    """

    def __init__(self, _info: Optional[dict[int, dict[str, PyAnn | CPPAnn]]] = None):
        """Stores _info dict which contains ribs in

        This is passed in so that we can regenerate this class from yaml

        Note that we do not use a defaultdict here because that is not
        yamlable using the yamlable library
        """

        # {neighbor: {prefix: announcement}}
        self._info: dict[int, dict[str, PyAnn | CPPAnn]] = (
            _info if _info is not None else dict()
        )

    def get_ann(self, neighbor_asn: int, prefix: str) -> Optional[PyAnn | CPPAnn]:
        """Returns Ann for a given neighbor asn and prefix"""

        return self._info.get(neighbor_asn, dict()).get(prefix)

    def add_ann(self, neighbor_asn: int, ann: PyAnn | CPPAnn) -> None:
        """Adds announcement to the ribs out"""

        if neighbor_asn in self._info:
            self._info[neighbor_asn][ann.prefix] = ann
        else:
            self._info[neighbor_asn] = {ann.prefix: ann}

    def remove_entry(self, neighbor_asn: int, prefix: str) -> None:
        """Removes ann from ribs out"""

        del self._info[neighbor_asn][prefix]

    def neighbors(self) -> Iterator[int]:
        """Return all neighbors from the ribs out"""

        return self._info.keys()  # type: ignore
