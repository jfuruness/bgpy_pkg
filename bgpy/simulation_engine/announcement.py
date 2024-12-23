from dataclasses import asdict, dataclass, replace
from typing import Any, Optional
from warnings import warn

from yamlable import YamlAble, yaml_info

from bgpy.shared.enums import Relationships


@yaml_info(yaml_tag="Announcement")
@dataclass(slots=True, frozen=True)
class Announcement(YamlAble):
    """BGP Announcement"""

    prefix: str
    as_path: tuple[int, ...]
    # Equivalent to the next hop in a normal BGP announcement
    next_hop_asn: int = None  # type: ignore
    seed_asn: int | None = None
    recv_relationship: Relationships = Relationships.ORIGIN

    #############################
    # Optional attributes below #
    #############################
    # If you aren't using the policies listed below,
    # You can create an announcement class without them
    # for a much faster runtime. Announcement copying is
    # the bottleneck for BGPy, smaller announcements copy
    # much faster across the AS topology

    # This currently is unused. Depending on some results from
    # our in-progress publications it may be used in the future
    # For now, we just set the timestamp of the victim to 0,
    # and timestamp of the attacker to 1
    timestamp: int = 0
    # Used for classes derived from BGPFull
    withdraw: bool = False
    # BGPsec optional attributes
    # BGPsec next ASN that should receive the control plane announcement
    # NOTE: this is the opposite direction of next_hop, for the data plane
    bgpsec_next_asn: int | None = None
    bgpsec_as_path: tuple[int, ...] = ()
    # RFC 9234 OTC attribute (Used in OnlyToCustomers Policy)
    only_to_customers: int | None = None
    # ROV++ attribute
    rovpp_blackhole: bool = False

    def __post_init__(self):
        """Defaults seed_asn and next_hop_asn"""

        # Since this gets called with replace where seed_asn None is valid,
        # can't do any other checks. Even this should prob be moved out due to
        # unessecary overhead
        if len(self.as_path) == 1 and self.seed_asn is None:
            object.__setattr__(self, "seed_asn", self.as_path[0])

        if self.next_hop_asn is None:
            # next hop defaults to None, messing up the type
            if len(self.as_path) == 1:  # type: ignore
                object.__setattr__(self, "next_hop_asn", self.as_path[0])
            elif len(self.as_path) > 1:
                raise ValueError(
                    "Announcement was initialized with an AS path longer than 1 "
                    f"({self.as_path}) but the next_hop_asn is ambiguous. "
                    " next_hop_asn is where the traffic should route to next."
                    "Please add "
                    "the next_hop_asn to the initialization parameters "
                    f"for the announcement of prefix {self.prefix}"
                )
            else:
                # Path is either zero or some other case we didn't account for
                raise NotImplementedError

    def copy(
        self, overwrite_default_kwargs: dict[Any, Any] | None = None
    ) -> "Announcement":
        """Creates a new ann with proper sim attrs"""

        if overwrite_default_kwargs:
            # Mypy says it gets this wrong
            # https://github.com/microsoft/pyright/issues/1047#issue-705124399
            return replace(self, **overwrite_default_kwargs)
        else:
            return replace(self)

    def __str__(self) -> str:
        return f"{self.prefix} {self.as_path} {self.recv_relationship}"

    @property
    def origin(self) -> int:
        """Returns the origin of the announcement"""

        return self.as_path[-1]

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[str, Any]:
        """This optional method is called when you call yaml.dump()"""

        return asdict(self)

    @classmethod
    def __from_yaml_dict__(
        cls: type["Announcement"], dct: dict[str, Any], yaml_tag: Any
    ) -> "Announcement":
        """This optional method is called when you call yaml.load()"""

        return cls(**dct)

    ####################
    # Deprecated funcs #
    ####################

    def prefix_path_attributes_eq(self, ann: Optional["Announcement"]) -> bool:
        """Checks prefix and as path equivalency"""

        warn(
            "Please use (ann.prefix, ann.as_path) == (self.prefix, self.as_path) "
            "instead of ._ribs_out. "
            "This will be removed in a later version",
            category=DeprecationWarning,
            stacklevel=2,
        )
        if ann is None:
            return False
        elif isinstance(ann, Announcement):
            return (ann.prefix, ann.as_path) == (self.prefix, self.as_path)
        else:
            raise NotImplementedError

    def bgpsec_valid(self, asn: int) -> bool:
        """Returns True if valid by BGPSec else False"""

        warn(
            "Please call bgpsec_valid from the BGPSec class, not the Announcement. "
            "This will be removed in a later version",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.bgpsec_next_asn == asn and self.bgpsec_as_path == self.as_path
