class LocalRib(dict):
    """Local RIB for a BGP AS

    Done separately for easy comparisons in unit testing
    """

    __slots__ = []

    def assert_eq(self, other):
        """Checks equality of local ribs using prefix, origin, as_path, time"""

        if isinstance(other, LocalRib):
            # Done this way to get specifics about what's different
            for prefix, ann in self.items():
                other_ann = other[prefix]
                assert other_ann.prefix == ann.prefix, f"{other_ann}, {ann}"
                assert other_ann.origin == ann.origin, f"{other_ann}, {ann}"
                assert other_ann.as_path == ann.as_path, f"{other_ann}, {ann}"
                assert other_ann.timestamp == ann.timestamp, f"{other_ann}, {ann}"
            for prefix, ann in other.items():
                self_ann = self[prefix]
                assert self_ann.prefix == ann.prefix, f"{self_ann}, {ann}"
                assert self_ann.origin == ann.origin, f"{self_ann}, {ann}"
                assert self_ann.as_path == ann.as_path, f"{self_ann}, {ann}"
                assert self_ann.timestamp == ann.timestamp, f"{self_ann}, {ann}"
        else:
            raise NotImplementedError

    def __str__(self):
        """String method done to turn anns into strings"""

        string = "{"
        for k, v in self.items():
            string += f"{k}: {v}, "
        string += "}"
        return string
