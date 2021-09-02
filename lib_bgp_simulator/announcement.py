from .engine.relationships import Relationships


class Announcement:
    """MRT Announcement"""

    __slots__ = ["prefix", "timestamp", "as_path", "roa_validity",
                 "recv_relationship", "priority", "seed_asn"]

    def __init__(self,
                 prefix=None,
                 timestamp=None,
                 as_path=None,
                 seed_asn=None,
                 roa_validity=None):
        self.prefix = prefix
        self.timestamp = timestamp
        self.seed_asn = seed_asn
        self.as_path = as_path
        # Tuples are faster
        assert isinstance(self.as_path, tuple)
        self.roa_validity = roa_validity
        if len(as_path) == 1:
            # Where the announcement came from
            self.recv_relationship = Relationships.ORIGIN
        else:
            print("fix l8r")
            self.recv_relationship = Relationships.ORIGIN
            # Must set the relationship based on the actual relationship
            #raise NotImplementedError
        self.priority = None

    def __lt__(self, other):
        assert isinstance(other, Announcement)
        assert isinstance(self.priority, int), self.priority
        assert isinstance(other.priority, int), other.priority

        return self.priority < other.priority
        
    def seed(self, as_dict):
        """Seeds announcement at the proper AS

        Since this is the simulator engine, we should
        never have to worry about overlapping announcements
        """

        as_dict[self.seed_asn].local_rib[self.prefix] = self

    @property
    def origin(self):
        return self.as_path[-1]

    def __str__(self):
        return f"{self.prefix} {self.origin} {self.as_path}"
