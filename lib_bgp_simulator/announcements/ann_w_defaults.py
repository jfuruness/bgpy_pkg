from dataclasses import dataclass

from .announcement import Announcement
from ..enums import Relationships


# We set equal to false here so that it can inherit __eq__ from parent
@dataclass(eq=False, unsafe_hash=True)
class AnnWDefaults(Announcement):
    """Announcement with defaults, mainly for testing

    Note that this is slower than normal Ann due to no slots
    but we need this since Pypy3.9 doesn't support dataclasses with slots
    that have defaults.
    """

    prefix: str = None
    as_path: tuple = None
    timestamp: int = 0
    seed_asn: int = None
    roa_valid_length: bool = None
    roa_origin: int = None
    recv_relationship: Relationships = Relationships.CUSTOMERS
    withdraw: bool = False
    traceback_end: bool = False
    communities: tuple = tuple()
