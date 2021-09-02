from enum import Enum


class Relationships(Enum):
    __slots__ = []

    PROVIDERS = 0
    PEERS = 1
    # Customers have highest priority
    # Economic incentives first!
    CUSTOMERS = 2
    # Origin must always remain
    ORIGIN = 3
