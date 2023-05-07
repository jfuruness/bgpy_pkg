from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Tuple, Type, TYPE_CHECKING

from caida_collector_pkg import AS

from ...simulation_engine import Announcement
from ...simulation_engine import BGPSimpleAS


if TYPE_CHECKING:
    from .scenario_trial import ScenarioTrial

pseudo_base_cls_dict: Dict[Type[AS], Type[AS]] = dict()


class MISSINGAS(AS):
    pass


@dataclass(frozen=True)
class ScenarioConfig:
    """Contains information required to set up a scenario/attack

    Is reused for multiple trials (thus, frozen)
    """

    ScenarioTrialCls: Type["ScenarioTrial"]
    # This is the base type of announcement for this class
    # You can specify a different base ann
    AnnCls: Type[Announcement] = Announcement
    BaseASCls: Type[AS] = BGPSimpleAS
    # Fixed in post init, but can't show mypy for some reason
    AdoptASCls: Type[AS] = MISSINGAS
    num_attackers: int = 1
    num_victims: int = 1
    # Adoption is equal across these atributes of the engine
    adoption_subcategory_attrs: Tuple[str, ...] = (
        "stub_or_mh_asns",
        "etc_asns",
        "input_clique_asns",
    )
    # Attackers can be chosen from this attribute of the engine
    attacker_subcategory_attr: str = "stub_or_mh_asns"
    # Victims can be chosen from this attribute of the engine
    victim_subcategory_attr: str = "stub_or_mh_asns"
    # ASes that are hardcoded to specific values
    hardcoded_asn_cls_dict: Dict[int, Type[AS]] = field(default_factory=dict)

    def __post_init__(self):
        """Sets AdoptASCls if it is None

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
                name: str = f"Psuedo {self.BaseASCls.name}".replace(" ", "")
                PseudoBaseCls = type(name, (self.BaseASCls,), {"name": name})
                pseudo_base_cls_dict[self.BaseASCls] = PseudoBaseCls
                AdoptASCls = PseudoBaseCls
            object.__setattr__(self, "AdoptASCls", AdoptASCls)

    ##############
    # Yaml Funcs #
    ##############

    @property
    def _yamlable_hardcoded_asn_cls_dict(self) -> Dict[int, str]:
        """Converts non default as cls dict to a yamlable dict of asn: name"""

        return {
            asn: AS.subclass_to_name_dict[ASCls]
            for asn, ASCls in self.hardcoded_asn_cls_dict.items()
        }

    @staticmethod
    def _get_hardcoded_asn_cls_dict_from_yaml(yaml_dict) -> Dict[int, Type[AS]]:
        """Converts yamlified non_default_as_cls_dict back to normal asn: class"""

        return {asn: AS.name_to_subclass_dict[name] for asn, name in yaml_dict.items()}

    def __to_yaml_dict__(self) -> Dict[Any, Any]:
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
