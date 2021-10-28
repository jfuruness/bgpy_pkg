from dataclasses import dataclass

from .announcement import Announcement
from ..enums import ROAValidity, Relationships


# NOTE: this is slower than the normal ann due to lack of slots
# In python3.7, supported by pypy, dataclasses with slots can't have defaults
# We set equal to false here so that it can inherit __eq__ from parent
@dataclass(eq=False)
class AnnWDefaults(Announcement):
    prefix: str = None
    as_path: tuple = None
    timestamp: int = 0
    seed_asn: int = None
    roa_validity: ROAValidity = ROAValidity.UNKNOWN
    recv_relationship: Relationships = Relationships.CUSTOMERS
    withdraw: bool = False
    traceback_end: bool = False
    communities: tuple = tuple()
