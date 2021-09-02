from enum import Enum

# Enums below

class ASTypes(Enum):
    """Different types of AS policies"""

    BGP = 0

class Timestamps(Enum):
    """Different timestamps to use"""

    # Victim is always first
    VICTIM = 0
    ATTACKER = 1

class Prefixes(Enum):
    """Prefixes to use for attacks

    prefix always belongs to the victim
    """

    SUPERPREFIX = "1.0.0.0/8"
    # Prefix always belongs to victim
    PREFIX = "1.2.0.0/16"
    SUBPREFIX = "1.2.3.0/24"

class ASNs(Enum):
    """Default ASNs for various ASNs"""

    ATTACKER = 666
    VICTIM = 777
