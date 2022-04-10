from .ann_container import AnnContainer

from ...announcements import Announcement


class LocalRIB(AnnContainer):
    """Local RIB for a BGP AS"""

    __slots__ = ()

    def get_ann(self, prefix: str, default=None):
        """Returns announcement or none from the local rib by prefix"""

        return self._info.get(prefix, default)

    def add_ann(self, ann: Announcement):
        """Adds an announcement to local rib with prefix as key"""

        self._info[ann.prefix] = ann

    def remove_ann(self, prefix: str):
        """Removes announcement from local rib based on prefix"""

        del self._info[prefix]

    def prefix_anns(self):
        """Returns all prefixes and announcements zipped"""

        return self._info.items()
