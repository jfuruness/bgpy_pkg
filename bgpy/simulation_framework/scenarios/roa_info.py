from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ROAInfo:
    prefix: str
    origin: int
    max_length: int = None  # type: ignore

    def __post_init__(self):
        """Defaults max length to be that of the prefix length"""

        assert "/" in self.prefix, f"Not a CIDR {self.prefix}"  # type: ignore
        prefix_length = int(self.prefix.split("/")[-1])

        if self.max_length is None:
            object.__setattr__(self, "max_length", prefix_length)

        msg = (
            "Due to a bug in the ROAChecker, max length MUST be equal to the prefix "
            "length. This will be fixed in V9, but that likely will not be out until "
            "2025, and even then I will continue to support V8.\n"
            "To work around this - simply have a ROA for every prefix length, and that "
            "will have the same affect as a single ROA with a greater max length"
        )
        if self.max_length != self.prefix_length:
            raise ValueError(msg)

    @property
    def routed(self) -> bool:
        return self.origin != 0

    @property
    def non_routed(self) -> bool:
        return not self.routed
