from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any

from frozendict import frozendict
from roa_checker import ROA

from bgpy.shared.enums import ASGroups
from bgpy.simulation_engine import ASPA, ASRA, BGP, BGPiSecTransitive, Policy
from bgpy.simulation_engine import Announcement as Ann

if TYPE_CHECKING:
    from .scenario import Scenario


class MISSINGPolicy(Policy):
    name: str = "missing"


@dataclass(frozen=True)
class ScenarioConfig:
    """Contains information required to set up a scenario/attack

    Is reused for multiple trials (thus, frozen)
    """

    ScenarioCls: type["Scenario"]
    # Set in post_init
    propagation_rounds: int = None  # type: ignore
    # This is the base type of announcement for this class
    # You can specify a different base ann
    AnnCls: type[Ann] = Ann
    BasePolicyCls: type[Policy] = BGP
    # Fixed in post init, but can't show mypy for some reason
    AdoptPolicyCls: type[Policy] = MISSINGPolicy  # type: ignore
    # Used to override attacker's base policy class
    AttackerBasePolicyCls: type[Policy] | None = None
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
    # NOTE: This should really be hardcoded_policy_asn_cls_dict,
    # but this is a legacy name so not going to break backwards compatability
    hardcoded_asn_cls_dict: frozendict[int, type[Policy]] = field(
        default_factory=frozendict
    )
    # This is as a fallback if the AS is not adopting, select from this dict,
    # else use BasePolicyCls
    hardcoded_base_asn_cls_dict: frozendict[int, type[Policy]] = field(
        default_factory=frozendict
    )
    # Only necessary if coming from YAML or the test suite
    override_attacker_asns: frozenset[int] | None = None
    override_victim_asns: frozenset[int] | None = None
    override_adopting_asns: frozenset[int] | None = None
    override_announcements: tuple["Ann", ...] | None = None
    override_roas: tuple[ROA, ...] | None = None
    # If you'd like to add an extra CSV label you do so here
    # This only adds basically your own notes, isn't used for
    # anything in particular
    csv_label: str = ""
    # Defaults to the AdoptPolicyCls's name property in post_init
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
            # BGP-iSec needs this. NOTE: mypy thinks this is unreachable
            if (  # type: ignore
                issubclass(self.AdoptPolicyCls, BGPiSecTransitive)
            ):
                from bgpy.simulation_framework import ShortestPathPrefixHijack

                if issubclass(self.ScenarioCls, ShortestPathPrefixHijack):
                    prop_rounds = 2
                else:
                    prop_rounds = self.ScenarioCls.min_propagation_rounds
            else:
                prop_rounds = self.ScenarioCls.min_propagation_rounds

            # initially set to None so it could be defaulted here
            object.__setattr__(self, "propagation_rounds", prop_rounds)

        if self.ScenarioCls.min_propagation_rounds > self.propagation_rounds:
            raise ValueError(
                f"{self.ScenarioCls.__name__} requires a minimum of "
                f"{self.ScenarioCls.min_propagation_rounds} propagation rounds "
                f"but this scenario_config has only {self.propagation_rounds} "
                "propagation rounds"
            )

        if self.AdoptPolicyCls == MISSINGPolicy:
            object.__setattr__(self, "AdoptPolicyCls", self.BasePolicyCls)
        # Better error messages when setting this var
        if not isinstance(self.hardcoded_asn_cls_dict, frozendict):
            raise TypeError(
                "hardcoded_asn_cls_dict of ScenarioConfig is not frozendict "
                f"and is instead {type(self.hardcoded_asn_cls_dict)}. Please "
                "change the type to frozendict so that it is hashable"
            )

        if not self.scenario_label:
            object.__setattr__(self, "scenario_label", self.AdoptPolicyCls.name)

        self._set_AttackerBasePolicyCls()

    def _set_AttackerBasePolicyCls(self):
        # This is to assist with ShortestPathPrefixHijacks
        if issubclass(self.AdoptPolicyCls, ASPA) and not issubclass(
            self.AdoptPolicyCls, ASRA
        ):
            # Mypy thinks this is unreachable
            AttackerBasePolicyCls = getattr(  # type: ignore
                self.ScenarioCls, "RequiredASPAAttackerCls", None
            )
            object.__setattr__(self, "AttackerBasePolicyCls", AttackerBasePolicyCls)

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

    @property
    def _yamlable_hardcoded_base_asn_cls_dict(self) -> dict[int, str]:
        """Converts non default as cls dict to a yamlable dict of asn: name"""

        return {
            asn: Policy.subclass_to_name_dict[PolicyCls]
            for asn, PolicyCls in self.hardcoded_base_asn_cls_dict.items()
        }

    @staticmethod
    def _get_hardcoded_base_asn_cls_dict_from_yaml(
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
            elif k == "hardcoded_base_asn_cls_dict":
                yaml_dict[k] = self._yamlable_hardcoded_base_asn_cls_dict
            else:
                yaml_dict[k] = v
        return yaml_dict

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """This optional method is called when you call yaml.load()"""

        dct["hardcoded_asn_cls_dict"] = cls._get_hardcoded_asn_cls_dict_from_yaml(
            dct["hardcoded_asn_cls_dict"]
        )
        dct["hardcoded_base_asn_cls_dict"] = (
            cls._get_hardcoded_base_asn_cls_dict_from_yaml(
                dct["hardcoded_base_asn_cls_dict"]
            )
        )

        return cls(**dct)
