from typing import Optional

from frozendict import frozendict

from .ann_container import AnnContainer

from bgpy.simulation_engines.py_simulation_engine import Announcement as Ann


class LocalRIB(AnnContainer):
    """Local RIB for a BGP AS"""

    def __init__(self, _info: dict[str, Ann] = frozendict()):
        """Stores _info dict which contains local ribs

        This is passed in so that we can regenerate this class from yaml

        Note that we do not use a defaultdict here because that is not
        yamlable using the yamlable library
        """

        self._info: dict[str, Ann] = _info

    def get_ann(self, prefix: str, default: Optional[Ann] = None) -> Optional[Ann]:
        """Returns announcement or none from the local rib by prefix"""

        return self._info.get(prefix, default)

    def add_ann(self, ann: Ann):
        """Adds an announcement to local rib with prefix as key"""

        self._info[ann.prefix] = ann

    def remove_ann(self, prefix: str):
        """Removes announcement from local rib based on prefix"""

        del self._info[prefix]

    def prefix_anns(self):
        """Returns all prefixes and announcements zipped"""

        return self._info.items()

    def __str__(self) -> str:
        return str({k: str(v) for k, v in self._info.items()})
