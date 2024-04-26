import abc
from dataclasses import asdict, dataclass, field
from typing import Any, Optional, TYPE_CHECKING

from frozendict import frozendict

from bgpy.enums import ASGroups

from bgpy.simulation_engine import Announcement as Ann
from bgpy.simulation_engine import Policy
from bgpy.simulation_engine import BGP

from .preprocess_anns_funcs import noop, PREPROCESS_ANNS_FUNC_TYPE
from .roa_info import ROAInfo


if TYPE_CHECKING:
    from .scenario import Scenario

pseudo_base_cls_dict: dict[type[Policy], type[Policy]] = dict()


class MISSINGPolicy(Policy):
    name: str = "missing"
    pass


@dataclass(frozen=True)
class ScenarioConfig:
    """Contains information required to set up a scenario/attack

    Is reused for multiple trials (thus, frozen)
    """

    ScenarioCls: type["Scenario"]
    # Set in post_init
    propagation_rounds: int = None  # type: ignore
    preprocess_anns_func: PREPROCESS_ANNS_FUNC_TYPE = noop
    # This is the base type of announcement for this class
    # You can specify a different base ann
    AnnCls: type[Ann] = Ann
    BasePolicyCls: type[Policy] = BGP
    # Fixed in post init, but can't show mypy for some reason
    AdoptPolicyCls: type[Policy] = MISSINGPolicy  # type: ignore
    # Used to override attacker's base policy class
    AttackerBasePolicyCls: Optional[type[Policy]] = None
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
    hardcoded_asn_cls_dict: frozendict[int, type[Policy]] = field(
        # Mypy doesn't understand frozendict typing, just ignore it
        default_factory=frozendict  # type: ignore
    )
    # Only necessary if coming from YAML or the test suite
    override_attacker_asns: Optional[frozenset[int]] = None
    override_victim_asns: Optional[frozenset[int]] = None
    # For some reason mypy has trouble with empty frozendicts
    # So I've included that as a second option for typing purposes
    # (specifically with the tests)
    override_non_default_asn_cls_dict: Any = None
    # Unfortunately this causes lots of errors in mypy, even though
    # it's correct. No idea why it's failing here, possibly something
    # internal to frozendict. Either way, it doesn't matter, this is
    # pretty much only used within the tests, which would fail if this
    # was wrong anyways
    # override_non_default_asn_cls_dict: Union[
    #    Optional[frozendict[int, type[Policy]]],
    #    frozendict[str, None]
    # ] = None
    override_announcements: tuple["Ann", ...] = ()
    override_roa_infos: tuple[ROAInfo, ...] = ()
    # If you'd like to add an extra CSV label you do so here
    csv_label: str = ""
    # Deprecated param, don't use
    scenario_label: str = ""

    def __post_init__(self):
        """sets AdoptPolicyCls if it is None

        This is done to fix the following:
        Scenario 1 has 3 BGP Policyes and 1 AdoptCls
        Scenario 2 has no adopt classes, so 4 BGP
        Scenario 3 we want to run ROV++, but what were the adopting Policyes from
        scenario 1? We don't know anymore.
        Instead for scenario 2, we have 3 BGP Policyes and 1 Psuedo BGP Policy
        Then scenario 3 will still work as expected
        """

        if self.propagation_rounds is None:
            object.__setattr__(  # type: ignore
                self, "propagation_rounds", self.ScenarioCls.min_propagation_rounds
            )

        if self.ScenarioCls.min_propagation_rounds > self.propagation_rounds:
            raise ValueError(
                f"{self.ScenarioCls.__name__} requires a minimum of "
                f"{self.ScenarioCls.min_propagation_rounds} propagation rounds "
                f"but this scenario_config has only {self.propagation_rounds} "
                "propagation rounds"
            )

        if self.AdoptPolicyCls == MISSINGPolicy:
            # mypy says this is unreachable, which is wrong
            global pseudo_base_cls_dict  # type: ignore
            AdoptPolicyCls = pseudo_base_cls_dict.get(self.BasePolicyCls)
            if not AdoptPolicyCls:
                name: str = f"Pseudo {self.BasePolicyCls.name}".replace(" ", "")
                PseudoBaseCls = type(name, (self.BasePolicyCls,), {"name": name})
                pseudo_base_cls_dict[self.BasePolicyCls] = PseudoBaseCls
                # Must set for pickling purposes
                setattr(abc, name, PseudoBaseCls)
                AdoptPolicyCls = PseudoBaseCls
            object.__setattr__(self, "AdoptPolicyCls", AdoptPolicyCls)
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
            asn: Policy.subclass_to_name_dict[PolicyCls]
            for asn, PolicyCls in self.hardcoded_asn_cls_dict.items()
        }

    @staticmethod
    def _get_hardcoded_asn_cls_dict_from_yaml(
        yaml_dict,
    ) -> dict[int, type[Policy]]:
        """Converts yamlified non_default_as_cls_dict back to normal asn: class"""

        return {
            asn: Policy.name_to_subclass_dict[name] for asn, name in yaml_dict.items()
        }

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
