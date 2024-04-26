from abc import ABC, abstractmethod
from dataclasses import replace
import math
import random
from ipaddress import ip_network
from ipaddress import IPv4Network
from ipaddress import IPv6Network
from typing import Any, Optional, Type, Union

from frozendict import frozendict

from roa_checker import ROAChecker, ROAValidity

from bgpy.simulation_engine import Announcement as Ann
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_engine import Policy
from bgpy.enums import (
    SpecialPercentAdoptions,
)

from .preprocess_anns_funcs import noop, PREPROCESS_ANNS_FUNC_TYPE
from .roa_info import ROAInfo
from .scenario_config import ScenarioConfig

pseudo_base_cls_dict: dict[type[Policy], type[Policy]] = dict()


class Scenario(ABC):
    """Contains information regarding a scenario/attack

    This represents a single trial
    """

    min_propagation_rounds: int = 1

    def __init__(
        self,
        *,
        scenario_config: ScenarioConfig,
        percent_adoption: Union[float, SpecialPercentAdoptions] = 0,
        engine: Optional[BaseSimulationEngine] = None,
        prev_scenario: Optional["Scenario"] = None,
        preprocess_anns_func: PREPROCESS_ANNS_FUNC_TYPE = noop,
    ):
        """inits attrs

        Any kwarg prefixed with default is only required for the test suite/YAML
        """

        # Config's ScenarioCls must be the same as instantiated Scenario
        assert scenario_config.ScenarioCls == self.__class__, (
            "The config's scenario class is "
            f"{scenario_config.ScenarioCls.__name__}, but the scenario used is "
            f"{self.__class__.__name__}"
        )

        self.scenario_config: ScenarioConfig = scenario_config
        self.percent_adoption: Union[float, SpecialPercentAdoptions] = percent_adoption

        self.attacker_asns: frozenset[int] = self._get_attacker_asns(
            scenario_config.override_attacker_asns, engine, prev_scenario
        )

        self.victim_asns: frozenset[int] = self._get_victim_asns(
            scenario_config.override_victim_asns, engine, prev_scenario
        )

        POLICY_CLS_DCT = frozendict[int, type[Policy]]
        self.non_default_asn_cls_dict: POLICY_CLS_DCT = (
            self._get_non_default_asn_cls_dict(
                scenario_config.override_non_default_asn_cls_dict, engine, prev_scenario
            )
        )

        if self.scenario_config.override_announcements:
            self.announcements: tuple["Ann", ...] = (
                self.scenario_config.override_announcements
            )
            self.roa_infos: tuple[ROAInfo, ...] = (
                self.scenario_config.override_roa_infos
            )
        else:
            anns = self._get_announcements(engine=engine, prev_scenario=prev_scenario)
            self.roa_infos = self._get_roa_infos(
                announcements=anns, engine=engine, prev_scenario=prev_scenario
            )
            anns = self._add_roa_info_to_anns(
                announcements=anns, engine=engine, prev_scenario=prev_scenario
            )
            self.announcements = preprocess_anns_func(self, anns, engine, prev_scenario)

        self.ordered_prefix_subprefix_dict: dict[str, list[str]] = (
            self._get_ordered_prefix_subprefix_dict()
        )

        self.policy_classes_used: frozenset[Type[Policy]] = frozenset()

    #################
    # Get attackers #
    #################

    def _get_attacker_asns(
        self,
        override_attacker_asns: Optional[frozenset[int]],
        engine: Optional[BaseSimulationEngine],
        prev_scenario: Optional["Scenario"],
    ) -> frozenset[int]:
        """Returns attacker ASN at random"""

        # This is coming from YAML, do not recalculate
        if override_attacker_asns is not None:
            attacker_asns = override_attacker_asns
            branch = 0
        # Reuse the attacker from the last scenario for comparability
        elif (
            prev_scenario
            and prev_scenario.scenario_config.num_attackers
            == self.scenario_config.num_attackers
        ):
            attacker_asns = prev_scenario.attacker_asns
            branch = 1
        elif (
            prev_scenario
            and prev_scenario.scenario_config.num_attackers
            < self.scenario_config.num_attackers
        ):
            old_attacker_asns = prev_scenario.attacker_asns
            branch = 2
            assert engine
            possible_attacker_asns = self._get_possible_attacker_asns(
                engine, self.percent_adoption, prev_scenario
            )
            possible_attacker_asns = possible_attacker_asns.difference(
                old_attacker_asns
            )

            assert len(possible_attacker_asns) >= (
                self.scenario_config.num_attackers - len(old_attacker_asns)
            )
            # https://stackoverflow.com/a/15837796/8903959
            new_attacker_asns = frozenset(
                random.sample(
                    tuple(possible_attacker_asns),
                    self.scenario_config.num_attackers - len(old_attacker_asns),
                )
            )
            attacker_asns = old_attacker_asns | new_attacker_asns

        # This is being initialized for the first time
        else:
            branch = 3
            assert engine
            possible_attacker_asns = self._get_possible_attacker_asns(
                engine, self.percent_adoption, prev_scenario
            )

            assert len(possible_attacker_asns) >= self.scenario_config.num_attackers
            # https://stackoverflow.com/a/15837796/8903959
            attacker_asns = frozenset(
                random.sample(
                    tuple(possible_attacker_asns), self.scenario_config.num_attackers
                )
            )

        # Validate attacker asns
        err = f"Number of attackers is different from attacker length: Branch {branch}"
        assert len(attacker_asns) == self.scenario_config.num_attackers, err

        return attacker_asns

    def _get_possible_attacker_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: Union[float, SpecialPercentAdoptions],
        prev_scenario: Optional["Scenario"],
    ) -> frozenset[int]:
        """Returns possible attacker ASNs, defaulted from config"""

        possible_asns = engine.as_graph.asn_groups[
            self.scenario_config.attacker_subcategory_attr
        ]
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        return possible_asns

    ###############
    # Get Victims #
    ###############

    def _get_victim_asns(
        self,
        override_victim_asns: Optional[frozenset[int]],
        engine: Optional[BaseSimulationEngine],
        prev_scenario: Optional["Scenario"],
    ) -> frozenset[int]:
        """Returns victim ASN at random"""

        # This is coming from YAML, do not recalculate
        if override_victim_asns is not None:
            victim_asns = override_victim_asns
        # Reuse the victim from the last scenario for comparability
        elif prev_scenario:
            victim_asns = prev_scenario.victim_asns
        # This is being initialized for the first time
        else:
            assert engine
            possible_victim_asns = self._get_possible_victim_asns(
                engine, self.percent_adoption, prev_scenario
            )
            # https://stackoverflow.com/a/15837796/8903959
            victim_asns = frozenset(
                random.sample(
                    tuple(possible_victim_asns), self.scenario_config.num_victims
                )
            )

        err = "Number of victims is different from victim length"
        assert len(victim_asns) == self.scenario_config.num_victims, err

        return victim_asns

    def _get_possible_victim_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: Union[float, SpecialPercentAdoptions],
        prev_scenario: Optional["Scenario"],
    ) -> frozenset[int]:
        """Returns possible victim ASNs, defaulted from config"""

        possible_asns = engine.as_graph.asn_groups[
            self.scenario_config.victim_subcategory_attr
        ]
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        # Remove attackers from possible victims
        possible_asns = possible_asns.difference(self.attacker_asns)
        return possible_asns

    #######################
    # Adopting ASNs funcs #
    #######################

    def _get_non_default_asn_cls_dict(
        self,
        override_non_default_asn_cls_dict: Union[
            Optional[frozendict[int, type[Policy]]],
            # Must include due to mypy weirdness
            # about empty frozendicts
            frozendict[str, None],
        ],
        engine: Optional[BaseSimulationEngine],
        prev_scenario: Optional["Scenario"],
    ) -> frozendict[int, type[Policy]]:
        """Returns as class dict

        non_default_asn_cls_dict is a dict of asn: AdoptPolicyCls
        where you do __not__ include any of the BasePolicyCls,
        since that is the default

        By default, we use the previous engine input to maintain static
        adoption across trials
        """

        if override_non_default_asn_cls_dict is not None:
            # Must ignore type here since mypy doesn't understand frozendict
            return override_non_default_asn_cls_dict  # type: ignore
        # By default, use the last engine input to maintain static
        # adoption across the graph
        elif prev_scenario:
            non_default_asn_cls_dict = dict()
            for asn, OldPolicyCls in prev_scenario.non_default_asn_cls_dict.items():
                HardcodedCls = self.scenario_config.hardcoded_asn_cls_dict.get(asn)
                if HardcodedCls:
                    non_default_asn_cls_dict[asn] = HardcodedCls
                # If the ASN was of the adopting class of the last scenario,
                # Update the adopting Policy class for the new scenario
                elif OldPolicyCls == prev_scenario.scenario_config.AdoptPolicyCls:
                    non_default_asn_cls_dict[asn] = self.scenario_config.AdoptPolicyCls
                # # Otherwise keep the AS class as it was
                # # This is useful for things like ROV, etc...
                # else:
                #     non_default_asn_cls_dict[asn] = OldPolicyCls
                # If you are comparing two scenarios that have different hardcoded ASNs
                # Then the commented out methodology above no longer works (and I think
                # it was only set that way for older versions of BGPy, really it makes
                # no sense for the latest versions of BGPy
        # Randomly get adopting ases if it hasn't been set yet
        else:
            assert engine, "either yaml, prev_scenario, or engine must be set"
            non_default_asn_cls_dict = self._get_randomized_non_default_asn_cls_dict(
                engine
            )

        # Validate that this is only non_default ASes
        # This matters, because later this entire dict may be used for the next
        # scenario
        for asn, PolicyCls in non_default_asn_cls_dict.items():
            assert PolicyCls != self.scenario_config.BasePolicyCls, "No defaults!"

        return frozendict(non_default_asn_cls_dict)

    def _get_randomized_non_default_asn_cls_dict(
        self,
        engine: BaseSimulationEngine,
    ) -> dict[int, type[Policy]]:
        """Get adopting ASNs and non default ASNs

        By default, to get even adoption, adopt in each of the three
        subcategories
        """

        # Get the asn_cls_dict without randomized adoption
        asn_cls_dict = dict(self.scenario_config.hardcoded_asn_cls_dict)
        for asn in self._default_adopters:
            asn_cls_dict[asn] = self.scenario_config.AdoptPolicyCls

        # Randomly adopt in all three subcategories
        for subcategory in self.scenario_config.adoption_subcategory_attrs:
            asns = engine.as_graph.asn_groups[subcategory]
            # Remove ASes that are already pre-set
            # Ex: Attacker and victim
            # Ex: ROV Nodes (in certain situations)
            possible_adopters = asns.difference(self._preset_asns)

            # Get how many ASes should be adopting

            # Round for the start and end of the graph
            # (if 0 ASes would be adopting, have 1 as adopt)
            # (If all ASes would be adopting, have all -1 adopt)
            # This was a feature request, but it's not supported
            if self.percent_adoption == SpecialPercentAdoptions.ONLY_ONE:
                k = 1
            elif self.percent_adoption == SpecialPercentAdoptions.ALL_BUT_ONE:
                k = len(possible_adopters) - 1
            # Really used just for testing
            elif self.percent_adoption == 0:
                k = 0
            else:
                err = f"{self.percent_adoption}"
                assert isinstance(self.percent_adoption, float), err
                k = math.ceil(len(possible_adopters) * self.percent_adoption)

            # https://stackoverflow.com/a/15837796/8903959
            possible_adopters_tup = tuple(possible_adopters)
            try:
                for asn in random.sample(possible_adopters_tup, k):
                    asn_cls_dict[asn] = self.scenario_config.AdoptPolicyCls
            except ValueError:
                raise ValueError(f"{k} can't be sampled from {len(possible_adopters)}")
        return asn_cls_dict

    @property
    def _default_adopters(self) -> frozenset[int]:
        """By default, victim always adopts"""

        return self.victim_asns

    @property
    def _default_non_adopters(self) -> frozenset[int]:
        """By default, attacker always does not adopt"""

        return self.attacker_asns

    @property
    def _preset_asns(self) -> frozenset[int]:
        """ASNs that have a preset adoption policy"""

        # Returns the union of default adopters and non adopters
        hardcoded_asns = set(self.scenario_config.hardcoded_asn_cls_dict)
        return self._default_adopters | self._default_non_adopters | hardcoded_asns

    @property
    def _untracked_asns(self) -> frozenset[int]:
        """Returns ASNs that shouldn't be tracked by the metric tracker

        By default just the default adopters and non adopters
        """

        return self._default_adopters | self._default_non_adopters

    #############################
    # Engine Manipulation Funcs #
    #############################

    def setup_engine(
        self, engine: BaseSimulationEngine, prev_scenario: Optional["Scenario"] = None
    ) -> None:
        """Sets up engine"""

        self.policy_classes_used = engine.setup(
            self.announcements,
            self.scenario_config.BasePolicyCls,
            self.non_default_asn_cls_dict,
            prev_scenario,
            self.attacker_asns,
            self.scenario_config.AttackerBasePolicyCls,
        )

    ##################
    # Subclass Funcs #
    ##################

    @abstractmethod
    def _get_announcements(
        self,
        engine: Optional[BaseSimulationEngine] = None,
        prev_scenario: Optional["Scenario"] = None,
    ) -> tuple["Ann", ...]:
        """Returns announcements"""

        raise NotImplementedError

    def _get_roa_infos(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional[BaseSimulationEngine] = None,
        prev_scenario: Optional["Scenario"] = None,
    ) -> tuple[ROAInfo, ...]:
        """Returns a tuple of ROAInfo's

        Not abstract and by default does nothing for
        backwards compatability
        """
        return ()

    def _add_roa_info_to_anns(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional[BaseSimulationEngine] = None,
        prev_scenario: Optional["Scenario"] = None,
    ) -> tuple["Ann", ...]:
        """Adds ROA Info to Announcements"""

        if self.roa_infos:
            roa_checker = self._get_roa_checker()
            processed_anns = list()
            for ann in announcements:
                prefix = ip_network(ann.prefix)

                roa_origin = self._get_roa_origin(roa_checker, prefix, ann.origin)

                roa_valid_length = self._get_roa_valid_length(
                    roa_checker, prefix, ann.origin
                )

                processed_anns.append(
                    ann.copy(
                        {
                            "roa_valid_length": roa_valid_length,
                            "roa_origin": roa_origin,
                            # Must add these two since copy overwrites them by default
                            "seed_asn": ann.seed_asn,
                            "traceback_end": getattr(ann, "traceback_end", False),
                        }
                    )
                )
            return tuple(processed_anns)
        else:
            return announcements

    def pre_aggregation_hook(
        self,
        engine: "BaseSimulationEngine",
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        propagation_round: int,
    ) -> None:
        """Useful hook for changes/checks
        prior to results aggregation.
        """
        pass

    def post_propagation_hook(
        self,
        engine: "BaseSimulationEngine",
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        propagation_round: int,
    ) -> None:
        """Useful hook for post propagation"""

        pass

    ####################
    # ROA Helper funcs #
    ####################

    def _get_roa_checker(self) -> ROAChecker:
        """Returns ROAChecker populated with self.roa_infos"""

        roa_checker = ROAChecker()
        for roa in self.roa_infos:
            roa_checker.insert(ip_network(roa.prefix), roa.origin, roa.max_length)
        return roa_checker

    def _get_roa_origin(
        self, roa_checker: ROAChecker, prefix: IPv4Network | IPv6Network, origin: int
    ) -> Optional[int]:
        """Returns ROA origin"""

        # Get ROA origin
        roa = roa_checker.get_roa(prefix, origin)
        if roa:
            roa_origins = [x[0] for x in roa.origin_max_lengths]
            if len(set(roa_origins)) != 1:
                raise NotImplementedError
            else:
                [roa_origin] = roa_origins
                assert isinstance(roa_origin, int), "for mypy"
                return roa_origin
        else:
            return None

    def _get_roa_valid_length(
        self,
        roa_checker: ROAChecker,
        prefix: IPv4Network | IPv6Network,
        origin: int,
    ) -> Optional[bool]:
        """Returns ROA validity"""

        validity, _ = roa_checker.get_validity(prefix, origin)
        if validity in (
            ROAValidity.INVALID_LENGTH,
            ROAValidity.INVALID_LENGTH_AND_ORIGIN,
        ):
            return False
        elif validity == ROAValidity.UNKNOWN:
            return None
        elif validity in (ROAValidity.VALID, ROAValidity.INVALID_ORIGIN):
            return True
        else:
            raise NotImplementedError(f"Should never reach this {validity}")

    ################
    # Helper Funcs #
    ################

    def _get_ordered_prefix_subprefix_dict(self):
        """Saves a dict of prefix to subprefixes

        mypy was having a lot of trouble with this section
        thus the type ignores
        """

        prefixes = set([])
        for ann in self.announcements:
            prefixes.add(ann.prefix)
        # Do this here for speed
        prefixes: list[Union[IPv4Network, IPv6Network]] = [  # type: ignore
            ip_network(x) for x in prefixes
        ]
        # Sort prefixes with most specific prefix first
        # Note that this must be sorted for the traceback to get the
        # most specific prefix first
        prefixes = list(sorted(prefixes, key=lambda x: x.num_addresses))  # type: ignore

        prefix_subprefix_dict = {x: [] for x in prefixes}  # type: ignore
        for outer_prefix, subprefix_list in prefix_subprefix_dict.items():
            for prefix in prefixes:
                if (
                    prefix.subnet_of(outer_prefix)  # type: ignore
                    and prefix != outer_prefix
                ):
                    subprefix_list.append(str(prefix))
        # Get rid of ip_network
        return {str(k): v for k, v in prefix_subprefix_dict.items()}

    @property
    def json_label(self) -> str:
        """Label that will be used on the graph"""

        return (
            f"{self.scenario_config.BasePolicyCls.name} "
            "({self.scenario_config.AdoptPolicyCls.name} adopting)"
        )

    ##############
    # Yaml Funcs #
    ##############

    @property
    def _yamlable_non_default_asn_cls_dict(self) -> frozendict[int, str]:
        """Converts non default as cls dict to a yamlable dict of asn: name"""

        return frozendict(
            {
                asn: Policy.subclass_to_name_dict[PolicyCls]
                for asn, PolicyCls in self.non_default_asn_cls_dict.items()
            }
        )

    @staticmethod
    def _get_non_default_asn_cls_dict_from_yaml(
        yaml_dict,
    ) -> frozendict[int, type[Policy]]:
        """Converts yamlified non_default_asn_cls_dict back to normal asn: class"""

        return frozendict(
            {asn: Policy.name_to_subclass_dict[name] for asn, name in yaml_dict.items()}
        )

    def __to_yaml_dict__(self) -> dict[Any, Any]:
        """This optional method is called when you call yaml.dump()"""

        config_to_save = replace(
            self.scenario_config,
            override_attacker_asns=self.attacker_asns,
            override_victim_asns=self.victim_asns,
            # Need to break mypy here so that this can become yamlable
            # Afterwards we can reverse it in the from_yaml
            override_non_default_asn_cls_dict=(
                self._yamlable_non_default_asn_cls_dict  # type: ignore
            ),
            override_announcements=self.announcements,
        )

        return {
            "scenario_config": config_to_save,
            "percent_adoption": self.percent_adoption,
        }

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """This optional method is called when you call yaml.load()"""

        non_default_asn_cls_dict = cls._get_non_default_asn_cls_dict_from_yaml(
            dct["scenario_config"].override_non_default_asn_cls_dict
        )
        config_to_use = replace(
            dct["scenario_config"],
            override_non_default_asn_cls_dict=non_default_asn_cls_dict,
        )

        return cls(
            scenario_config=config_to_use,
            percent_adoption=dct["percent_adoption"],
        )
