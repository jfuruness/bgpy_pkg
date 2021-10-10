import inspect
from itertools import chain

from .enums import Relationships, ROAValidity


class Announcement:
    """MRT Announcement"""

    # I ran tests for 50 trials for 20% adoption for ROV
    # On average, with slots and pypy, an average of 207 seconds
    # But without slots, more RAM, but 175 seconds
    # I ran a lot of these trials and this was very consistent
    # extremely low standard deviation. Maybe 1s difference across trials
    # My thought is twofold. One is that maybe object creation with slots
    # Is slightly slower, but less RAM with faster attr access
    # Maybe this has to do with deepcopy doing better without slots
    # Or maybe pypy is more optimized without slots since it's more common
    # No reason to figure out exactly why, but turning off slots for
    # Slightly more RAM but slightly faster trials makes sense to me since
    # We have very few prefixes per attack. If that ever changes
    # Maybe it makes sense to add this back
    # Additionally, without slots, I tried making it according to the RFC
    # I added dicts for simulation attrs, path attrs, transitive, non trans
    # But this was much slower, 228 seconds
    # NOTE: All of this was when we were deep copying announcements instead of
    # Creating new ones from scratch. After creating new ones from scratch,
    # Trials were more than twice as fast, completing between 90-95s without slots
    # With slots, around 88-89s per trial. Not much of a difference, but also less ram
    # And it's just faster. We'd have to do larger timing tests to find out more
    # NOTE: also add prefix_id reasoning to design_decisions
    __slots__ = ["prefix", "timestamp", "as_path", "roa_validity",
                 "recv_relationship", "seed_asn", "withdraw", "traceback_end"]

    def __init__(self,
                 prefix=None,
                 as_path=None,
                 timestamp=None,
                 seed_asn=None,
                 # Ez requeset
                 roa_validity=ROAValidity.UNKNOWN,
                 recv_relationship=None,#Relationships.origin,
                 withdraw=False,
                 traceback_end=False):
        self.prefix = prefix
        self.as_path = as_path

        # Simulation attributes below

        self.timestamp = timestamp

        self.seed_asn = seed_asn
        # Tuples are faster
        assert isinstance(self.as_path, tuple)

        self.roa_validity = roa_validity
        assert isinstance(roa_validity, ROAValidity)

        self.recv_relationship = recv_relationship
        assert isinstance(recv_relationship, Relationships)

        self.withdraw = withdraw

        self.traceback_end = traceback_end

        # https://stackoverflow.com/a/427533/8903959
        #if "__slots__" not in inspect.getsource(self.__class__):
        #    raise Exception("Your ann class needs __slots__. See base class for ex.")

    def __eq__(self, other):
        if isinstance(other, Announcement):
            eq = True
            for attr in ["prefix", "as_path", "recv_relationship"]:
                if getattr(self, attr) != getattr(other, attr):
                    eq = False
            return eq
        else:
            raise NotImplementedError

    def seed(self, as_dict, propagation_round):
        """Seeds announcement at the proper AS

        Since this is the simulator engine, we should
        never have to worry about overlapping announcements
        """

        if propagation_round == 0:
            assert as_dict[self.seed_asn].local_rib.get_ann(self.prefix) is None, "Seeding conflict"

            as_dict[self.seed_asn].local_rib.add_ann(self)#[self.prefix] = self

    def prefix_path_attributes_eq(self, ann):
        """Checks prefix and as path equivalency"""

        if ann is None:
            return False
        elif isinstance(ann, Announcement):
            return (ann.prefix, ann.as_path) == (self.prefix, self.as_path)
        else:
            raise NotImplementedError

    def copy(self, cls=None, **extra_kwargs):
        """Creates a new ann with proper sim attrs"""

        kwargs = self.default_copy_kwargs
        # This is for subclasses to have their own attrs here
        kwargs.update(extra_kwargs)

        prefix = kwargs.pop("prefix")

        if cls is None:
            cls = self.__class__

        return cls(prefix, **kwargs)

    @property
    def default_copy_kwargs(self):

        # Gets all slots from parent classes and this class
        # https://stackoverflow.com/a/6720815/8903959
        slots = chain.from_iterable(getattr(cls, '__slots__', [])
                                            for cls in self.__class__.__mro__)

        kwargs = {attr: getattr(self, attr) for attr in slots}
        kwargs["seed_asn"] = None
        kwargs["traceback_end"] = False
        return kwargs

    @property
    def origin(self):
        return self.as_path[-1]

    def __str__(self):
        return f"{self.prefix} {self.as_path} {self.recv_relationship}"
