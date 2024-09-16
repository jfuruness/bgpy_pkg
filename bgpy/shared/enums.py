from enum import Enum, unique

yamlable_enums: list[type["YamlAbleEnum"]] = []


# Yaml must have unique keys/values
@unique
class YamlAbleEnum(Enum):
    def __init_subclass__(cls: type["YamlAbleEnum"], *args, **kwargs) -> None:
        """This method essentially creates a list of all subclasses

        This is used later in the yaml codec
        """

        super().__init_subclass__(*args, **kwargs)
        yamlable_enums.append(cls)

    @classmethod
    def yaml_suffix(cls: type["YamlAbleEnum"]) -> str:
        return cls.__name__

    @staticmethod
    def yamlable_enums() -> list[type["YamlAbleEnum"]]:
        return yamlable_enums


class Outcomes(YamlAbleEnum):
    ATTACKER_SUCCESS: int = 0
    VICTIM_SUCCESS: int = 1
    DISCONNECTED: int = 2
    UNDETERMINED: int = 3


class Relationships(YamlAbleEnum):
    # Must start at one for the priority
    PROVIDERS: int = 1
    PEERS: int = 2
    # Customers have highest priority
    # Economic incentives first!
    CUSTOMERS: int = 3
    # Origin must always remain
    ORIGIN: int = 4
    # Unknown for external programs like extrapoaltor
    UNKNOWN: int = 5


class Plane(YamlAbleEnum):
    # Changing to integers so that this is compatible with c++
    DATA: int = 0  # "data_plane"
    CTRL: int = 1  # "control_plane"


class ROAValidity(YamlAbleEnum):
    """Possible values for ROA Validity

    Note that we cannot differentiate between
    invalid by origin or max length
    because you could get one that is invalid by origin for one roa
    and invalid by max length for another roa
    """

    VALID: int = 0
    UNKNOWN: int = 1
    INVALID: int = 2


class Timestamps(YamlAbleEnum):
    """Different timestamps to use"""

    # Victim is always first
    VICTIM: int = 0
    ATTACKER: int = 1


class Prefixes(YamlAbleEnum):
    """Prefixes to use for attacks

    prefix always belongs to the victim
    """

    SUPERPREFIX: str = "1.0.0.0/8"
    # Prefix always belongs to victim
    PREFIX: str = "1.2.0.0/16"
    SUBPREFIX: str = "1.2.3.0/24"


class ASNs(YamlAbleEnum):
    """Default ASNs for various ASNs"""

    ATTACKER: int = 666
    VICTIM: int = 777


class ASGroups(YamlAbleEnum):
    """AS types"""

    IXPS: str = "ixp"
    # NOTE: only the IXP group has IXPs
    STUBS: str = "stub"
    MULTIHOMED: str = "multihomed"
    STUBS_OR_MH: str = "stub_or_multihomed"
    INPUT_CLIQUE: str = "input_clique"
    # Not stubs, multihomed, or input clique
    ETC: str = "etc"
    # not stubs or multihomed
    TRANSIT: str = "transit"
    ALL_WOUT_IXPS: str = "all_wout_ixps"


class SpecialPercentAdoptions(YamlAbleEnum):
    ALL_BUT_ONE: float = 1
    ONLY_ONE: float = 0

    def __float__(self) -> float:
        return float(self.value)

    def __lt__(self, other):
        if isinstance(other, (SpecialPercentAdoptions, float)):
            return float(self) == float(other)
        else:
            return NotImplemented


class InAdoptingASNs(YamlAbleEnum):
    TRUE: str = "True"
    FALSE: str = "False"
    ANY: str = "Any"
