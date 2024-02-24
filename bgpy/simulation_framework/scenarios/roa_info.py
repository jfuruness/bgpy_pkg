from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ROAInfo:
    prefix: str
    origin: int
    max_length: int
