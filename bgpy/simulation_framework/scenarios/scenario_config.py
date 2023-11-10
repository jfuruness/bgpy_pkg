import abc
from dataclasses import asdict, dataclass, field
from typing import Any, Optional, Union, TYPE_CHECKING

from frozendict import frozendict

from bgpy.caida_collector import AS
from bgpy.enums import ASGroups

from bgpy.simulation_engine import Announcement
from bgpy.simulation_engine import BGPSimpleAS


if TYPE_CHECKING:
    from .scenario_trial import Scenario

pseudo_base_cls_dict: dict[type[AS], type[AS]] = dict()


class MISSINGAS(AS):
    pass


@dataclass(frozen=True)
class ScenarioConfig:
    """Contains information required to set up a scenario/attack

    Is reused for multiple trials (thus, frozen)
    """

    ScenarioCls: type["Scenario"]
    # This is the base type of announcement for this class
    # You can specify a different base ann
    AnnCls: type[Announcement] = Announcement
    BaseASCls: type[AS] = BGPSimpleAS
    # Fixed in post init, but can't show mypy for some reason
    AdoptASCls: type[AS] = MISSINGAS
    num_attackers: int = 1
    num_victims: int = 1
    # Adoption is equal across these atributes of the engine
    adoption_subcategory_attrs: tuple[str, ...] = (
        ASGroups.STUBS_OR_MH.value,
        ASGroups.ETC.value,
        ASGroups.INPUT_CLIQUE.value,
    )
    # Attackers can be chosen from this attribute of the engine
    attacker_subcategory_attr: str = ASGroups.STUBS_OR_MH.value
    # Victims can be chosen from this attribute of the engine
    victim_subcategory_attr: str = ASGroups.STUBS_OR_MH.value
    # ASes that are hardcoded to specific values
    hardcoded_asn_cls_dict: frozendict[int, type[AS]] = field(
        # Mypy doesn't understand frozendict typing, just ignore it
        default_factory=frozendict  # type: ignore
    )
    # Only necessary if coming from YAML or the test suite
    override_attacker_asns: Optional[frozenset[int]] = None
    override_victim_asns: Optional[frozenset[int]] = None
    # For some reason mypy has trouble with empty frozendicts
    # So I've included that as a second option for typing purposes
    # (specifically with the tests)
    override_non_default_asn_cls_dict: Union[
        Optional[frozendict[int, type[AS]]], frozendict[str, None]
    ] = None
    override_announcements: tuple[Announcement, ...] = ()
    # If you'd like to add an extra CSV label you do so here
    csv_label: str = ""
    # Deprecated param, don't use
    scenario_label: str = ""

    def __post_init__(self):
        """sets AdoptASCls if it is None

        This is done to fix the following:
        Scenario 1 has 3 BGP ASes and 1 AdoptCls
        Scenario 2 has no adopt classes, so 4 BGP
        Scenario 3 we want to run ROV++, but what were the adopting ASes from
        scenario 1? We don't know anymore.
        Instead for scenario 2, we have 3 BGP ASes and 1 Psuedo BGP AS
        Then scenario 3 will still work as expected
        """

        if self.AdoptASCls == MISSINGAS:
            # mypy says this is unreachable, which is wrong
            global pseudo_base_cls_dict  # type: ignore
            AdoptASCls = pseudo_base_cls_dict.get(self.BaseASCls)
            if not AdoptASCls:
                name: str = f"Pseudo {self.BaseASCls.name}".replace(" ", "")
                PseudoBaseCls = type(name, (self.BaseASCls,), {"name": name})
                pseudo_base_cls_dict[self.BaseASCls] = PseudoBaseCls
                # Must set for pickling purposes
                setattr(abc, name, PseudoBaseCls)
                AdoptASCls = PseudoBaseCls
            object.__setattr__(self, "AdoptASCls", AdoptASCls)
        # Better error messages when setting this var
        if not isinstance(self.hardcoded_asn_cls_dict, frozendict):  # type: ignore
            raise TypeError(
                "hardcoded_asn_cls_dict of ScenarioConfig is not frozendict "
                f"and is instead {type(self.hardcoded_asn_cls_dict)}. Please "
                "change the type to frozendict so that it is hashable"
            )

    ##############
    # Yaml Funcs #
    ##############

    @property
    def _yamlable_hardcoded_asn_cls_dict(self) -> dict[int, str]:
        """Converts non default as cls dict to a yamlable dict of asn: name"""

        return {
            asn: AS.subclass_to_name_dict[ASCls]
            for asn, ASCls in self.hardcoded_asn_cls_dict.items()
        }

    @staticmethod
    def _get_hardcoded_asn_cls_dict_from_yaml(yaml_dict) -> dict[int, type[AS]]:
        """Converts yamlified non_default_as_cls_dict back to normal asn: class"""

        return {asn: AS.name_to_subclass_dict[name] for asn, name in yaml_dict.items()}

    def __to_yaml_dict__(self) -> dict[Any, Any]:
        """This optional method is called when you call yaml.dump()"""

        yaml_dict = dict()
        for k, v in asdict(self).items():
            if k == "hardcoded_asn_cls_dict":
                yaml_dict[k] = self._yamlable_hardcoded_asn_cls_dict
            else:
                yaml_dict[k] = v
        return yaml_dict

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """This optional method is called when you call yaml.load()"""

        dct["hardcoded_asn_cls_dict"] = cls._get_hardcoded_asn_cls_dict_from_yaml(
            dct["hardcoded_asn_cls_dict"]
        )
        return cls(**dct)
