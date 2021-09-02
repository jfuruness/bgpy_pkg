from enum import Enum

class ROAValidity(Enum):
    """Possible values for ROA Validity

    Note that we cannot differentiate between
    invalid by origin or max length
    because you could get one that is invalid by origin for one roa
    and invalid by max length for another roa
    """

    VALID = 0
    UNKNOWN = 1
    INVALID = 2
