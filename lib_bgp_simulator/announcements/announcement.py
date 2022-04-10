import dataclasses

from yamlable import YamlAble, yaml_info, yaml_info_decorate

from ..enums import Relationships


# Because of the two issues below, we MUST use
# unsafe_hash and not frozen
# We can't use their backports
# Because we inherit announcements
# So the slots in an announcement != vars
# When python3.10 is supported by pypy3, we can
# use Frozen properly
# https://stackoverflow.com/q/55307017/8903959
# https://bugs.python.org/issue45520
@yaml_info(yaml_tag="Announcement")
@dataclasses.dataclass(unsafe_hash=True)
class Announcement(YamlAble):
    """BGP Announcement"""

    # MUST use slots for speed
    # Since anns get copied across 70k ASes
    __slots__ = ("prefix", "timestamp", "as_path", "roa_valid_length",
                 "roa_origin",
                 "recv_relationship", "seed_asn", "withdraw", "traceback_end")

    # NOTE: can't have defaults due to slots. Sorry man
    # https://stackoverflow.com/a/50180784/8903959
    prefix: str
    as_path: tuple
    timestamp: int
    seed_asn: int
    roa_valid_length: bool
    roa_origin: int
    recv_relationship: Relationships
    withdraw: bool
    traceback_end: bool
    communities: tuple

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to easily assign yaml tags
        """

        super().__init_subclass__(*args, **kwargs)
        yaml_info_decorate(cls, yaml_tag=cls.__name__)

    def __eq__(self, other):
        if isinstance(other, Announcement):
            return dataclasses.asdict(self) == dataclasses.asdict(other)
        else:
            return NotImplemented

    def prefix_path_attributes_eq(self, ann):
        """Checks prefix and as path equivalency"""

        if ann is None:
            return False
        elif isinstance(ann, Announcement):
            return (ann.prefix, ann.as_path) == (self.prefix, self.as_path)
        else:
            raise NotImplementedError

    def copy(self, **extra_kwargs):
        """Creates a new ann with proper sim attrs"""

        # Replace seed asn and traceback end every time by default
        kwargs = {"seed_asn": None, "traceback_end": False}
        kwargs.update(extra_kwargs)

        return dataclasses.replace(self, **kwargs)

    @property
    def invalid_by_roa(self) -> bool:
        """Returns True if Ann is invalid by ROA

        False means ann is either valid or unknown
        """

        # Not covered by ROA, unknown
        if self.roa_origin is None:
            return False
        else:
            return self.origin != self.roa_origin or not self.roa_valid_length

    @property
    def valid_by_roa(self) -> bool:
        """Returns True if Ann is valid by ROA

        False means ann is either invalid or unknown
        """

        return self.origin == self.roa_origin and self.roa_valid_length

    @property
    def unknown_by_roa(self) -> bool:
        """Returns True if ann is not covered by roa"""

        return self.origin is None

    @property
    def covered_by_roa(self):
        """Returns if an announcement has a roa"""

        return not self.unknown_by_roa

    @property
    def roa_routed(self):
        """Returns bool for if announcement is routed according to ROA"""

        return self.roa_origin != 0

    @property
    def origin(self) -> int:
        """Returns the origin of the announcement"""

        return self.as_path[-1]

    def __str__(self):
        return f"{self.prefix} {self.as_path} {self.recv_relationship}"

##############
# Yaml funcs #
##############

    def __to_yaml_dict__(self):
        """ This optional method is called when you call yaml.dump()"""

        return dataclasses.asdict(self)

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """ This optional method is called when you call yaml.load()"""

        return cls(**dct)
