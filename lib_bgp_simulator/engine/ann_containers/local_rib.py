from ...announcement import Announcement

class LocalRib:
    """Local RIB for a BGP AS

    Done separately for easy comparisons in unit testing
    """

    __slots__ = ["_info"]

    def __init__(self):
        self._info = dict()

    def __eq__(self, other):
        # Remove this after updating the system tests
        if isinstance(other, dict):
            return self._info == other
        elif isinstance(other, LocalRib):
            return self._info == other._info
        else:
            raise NotImplementedError

    def get_ann(self, prefix, default=None):
        assert isinstance(prefix, str)
        return self._info.get(prefix, default)

    def add_ann(self, ann):
        assert isinstance(ann, Announcement)

        self._info[ann.prefix] = ann

    def remove_ann(self, prefix):
        del self._info[prefix]

    def prefix_anns(self):
        return self._info.items()

    def __str__(self):
        """String method done to turn anns into strings"""

        string = "{"
        for k, v in self._info.items():
            string += f"{k}: {v}, "
        string += "}"
        return string
