from enum import Enum


class Outcomes(Enum):
    ATTACKER_SUCCESS = 0
    VICTIM_SUCCESS = 1
    DISCONNECTED = 2


class Relationships(Enum):
    __slots__ = []

    # Must start at one for the priority
    PROVIDERS = 100
    PEERS = 200
    # Customers have highest priority
    # Economic incentives first!
    CUSTOMERS = 300
    # Origin must always remain
    ORIGIN = 400

# Assert here all divisible by 100

class ROAValidity(Enum):
    """Possible values for ROA Validity

    Note that we cannot differentiate between
    invalid by origin or max length
    because you could get one that is invalid by origin for one roa
    and invalid by max length for another roa
    """

    __slots__ = []

    VALID = 0
    UNKNOWN = 1
    INVALID = 2

class Timestamps(Enum):
    """Different timestamps to use"""

    __slots__ = []

    # Victim is always first
    VICTIM = 0
    ATTACKER = 1


class Prefixes(Enum):
    """Prefixes to use for attacks

    prefix always belongs to the victim
    """

    __slots__ = []

    SUPERPREFIX = "1.0.0.0/8"
    # Prefix always belongs to victim
    PREFIX = "1.2.0.0/16"
    SUBPREFIX = "1.2.3.0/24"

class ASNs(Enum):
    """Default ASNs for various ASNs"""

    __slots__ = []

    ATTACKER = 666
    VICTIM = 777

