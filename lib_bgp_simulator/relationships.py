from enum import Enum


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
