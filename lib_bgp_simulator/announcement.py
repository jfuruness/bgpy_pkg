from .enums import Relationships


class Announcement:
    """MRT Announcement"""

    __slots__ = ["prefix", "timestamp", "as_path", "roa_validity",
                 "recv_relationship", "seed_asn", "withdraw"]

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
        self.withdraw = False

    def seed(self, as_dict, propagation_round):
        """Seeds announcement at the proper AS

        Since this is the simulator engine, we should
        never have to worry about overlapping announcements
        """

        if propagation_round == 0:
            assert as_dict[self.seed_asn].policy.local_rib.get(self.prefix) is None, "Seeding conflict"
            as_dict[self.seed_asn].policy.local_rib[self.prefix] = self

    def prefix_path_attributes_eq(self, ann):
        """Checks prefix and as path equivalency"""

        if ann is None:
            return False
        elif isinstance(ann, Announcement):
            return (ann.prefix, ann.as_path) == (self.prefix, self.as_path)
        else:
            raise NotImplementedError

    @property
    def origin(self):
        return self.as_path[-1]

    def __str__(self):
        return f"{self.prefix} {self.origin} {self.as_path}"
