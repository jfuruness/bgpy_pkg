from typing import Any, Optional

from bgpy.shared.enums import Relationships


class BGPAnn:
    """Smaller BGP Announcement for speed, compatible with only BGP"""

    __slots__ = ("prefix", "next_hop_asn", "as_path", "seed_asn", "recv_relationship")

    def __init__(
        self,
        *,
        prefix: str,
        as_path: tuple[int],
        next_hop_asn: int = None,  # type: ignore
        seed_asn: Optional[int] = None,
        recv_relationship: Relationships = Relationships.ORIGIN,
        **kwargs,
    ) -> None:
        self.prefix = prefix
        self.as_path = as_path
        self.recv_relationship = recv_relationship
        self.seed_asn = seed_asn
        self.next_hop_asn = next_hop_asn
        # Since this gets called with replace where seed_asn None is valid,
        # can't do any other checks. Even this should prob be moved out due to
        # unessecary overhead
        if len(self.as_path) == 1 and self.seed_asn is None:
            self.seed_asn = self.as_path[0]

        if self.next_hop_asn is None:
            # next hop defaults to None, messing up the type
            if len(self.as_path) == 1:  # type: ignore
                self.next_hop_asn = self.as_path[0]
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
        self, overwrite_default_kwargs: Optional[dict[Any, Any]] = None
    ) -> "SmallAnn":
        """Creates a new ann with proper sim attrs

        NOTE: This won't work with subclasses due to __slots__
        """

        # Replace seed asn and traceback end every time by default
        kwargs = {
            "prefix": self.prefix,
            "as_path": self.as_path,
            "next_hop_asn": self.next_hop_asn,
            "seed_asn": None,
            "recv_relationship": self.recv_relationship,
        }

        if overwrite_default_kwargs:
            kwargs.update(overwrite_default_kwargs)

        return self.__class__(**kwargs)

    @property
    def origin(self) -> int:
        """Returns the origin of the announcement"""

        return self.as_path[-1]

    def prefix_path_attributes_eq(self, ann: Optional["Announcement"]) -> bool:
        """Checks prefix and as path equivalency"""

        if ann is None:
            return False
        else:
            return (ann.prefix, ann.as_path) == (self.prefix, self.as_path)

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[str, Any]:
        """This optional method is called when you call yaml.dump()"""

        return dict(vars(self))

    @classmethod
    def __from_yaml_dict__(
        cls: type["Announcement"], dct: dict[str, Any], yaml_tag: Any
    ) -> "Announcement":
        """This optional method is called when you call yaml.load()"""

        return cls(**dct)
