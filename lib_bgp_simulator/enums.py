from enum import Enum, unique


yamlable_enums = []

# Yaml must have unique keys/values
@unique
class YamlAbleEnum(Enum):

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses

        This is used later in the yaml codec
        """

        super().__init_subclass__(*args, **kwargs)
        yamlable_enums.append(cls)

    @classmethod
    def yaml_tag(cls):
        return f"!{cls.__name__}"

    @staticmethod
    def yamlable_enums():
        return yamlable_enums


class Outcomes(YamlAbleEnum):
    __slots__ = tuple()

    ATTACKER_SUCCESS = 0
    VICTIM_SUCCESS = 1
    DISCONNECTED = 2


class Relationships(YamlAbleEnum):
    __slots__ = tuple()

    # Must start at one for the priority
    PROVIDERS = 1
    PEERS = 2
    # Customers have highest priority
    # Economic incentives first!
    CUSTOMERS = 3
    # Origin must always remain
    ORIGIN = 4


class ROAValidity(YamlAbleEnum):
    """Possible values for ROA Validity

    Note that we cannot differentiate between
    invalid by origin or max length
    because you could get one that is invalid by origin for one roa
    and invalid by max length for another roa
    """

    __slots__ = tuple()

    VALID = 0
    UNKNOWN = 1
    INVALID = 2


class Timestamps(YamlAbleEnum):
    """Different timestamps to use"""

    __slots__ = tuple()

    # Victim is always first
    VICTIM = 0
    ATTACKER = 1


class Prefixes(YamlAbleEnum):
    """Prefixes to use for attacks

    prefix always belongs to the victim
    """

    __slots__ = tuple()

    SUPERPREFIX = "1.0.0.0/8"
    # Prefix always belongs to victim
    PREFIX = "1.2.0.0/16"
    SUBPREFIX = "1.2.3.0/24"

class ASNs(YamlAbleEnum):
    """Default ASNs for various ASNs"""

    __slots__ = tuple()

    ATTACKER = 666
    VICTIM = 777
