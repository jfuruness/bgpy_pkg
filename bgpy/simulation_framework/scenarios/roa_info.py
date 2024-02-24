from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ROAInfo:
    prefix: str
    origin: int
    max_length: int = None  # type: ignore

    def __post_init__(self):
        """Defaults max length to be that of the prefix length"""

        if self.max_length is None:
            assert "/" in self.prefix, f"Not a CIDR {self.prefix}"  # type: ignore
            object.__setattr__(self, "max_length", int(self.prefix.split("/")[-1]))
