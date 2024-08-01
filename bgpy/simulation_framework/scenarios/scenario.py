from abc import ABC, abstractmethod
from dataclasses import replace
from functools import cached_property
from ipaddress import ip_network
from ipaddress import IPv4Network
from ipaddress import IPv6Network
import math
import random
from typing import Any, Optional, Type, TYPE_CHECKING, Union


from roa_checker import ROAChecker, ROAValidity, ROA

from bgpy.simulation_engine import Announcement as Ann
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_engine import Policy
from bgpy.enums import (
    SpecialPercentAdoptions,
)

from .preprocess_anns_funcs import noop, PREPROCESS_ANNS_FUNC_TYPE
from .scenario_config import ScenarioConfig

if TYPE_CHECKING:
    from bgpy.as_graphs import AS


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
        preprocess_anns_func: PREPROCESS_ANNS_FUNC_TYPE = noop,
        attacker_asns: Optional[frozenset[int]] = None,
        victim_asns: Optional[frozenset[int]] = None,
        adopting_asns: Optional[frozenset[int]] = None,
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
            scenario_config.override_attacker_asns,
            attacker_asns,
            engine,
        )

        self.victim_asns: frozenset[int] = self._get_victim_asns(
            scenario_config.override_victim_asns, victim_asns, engine
        )
        raise NotImplementedError("Destroy these adoption funcs")
        self.adopting_asns: frozenset[int] = self._get_adopting_asns(
            scenario_config.override_adopting_asns,
            adopting_asns,
            engine,
        )

        if self.scenario_config.override_announcements:
            self.announcements: tuple["Ann", ...] = (
                self.scenario_config.override_announcements
            )
            self.roas: tuple[ROA, ...] = self.scenario_config.override_roas
        else:
            anns = self._get_announcements(engine=engine)
            self.roas = self._get_roas(announcements=anns, engine=engine)
            anns = self._add_roa_info_to_anns(announcements=anns, engine=engine)
            self.announcements = preprocess_anns_func(self, anns, engine)

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
        prev_attacker_asns: Optional[frozenset[int]],
        engine: Optional[BaseSimulationEngine],
    ) -> frozenset[int]:
        """Returns attacker ASN at random"""

        # This is coming from YAML, do not recalculate
        if override_attacker_asns is not None:
            attacker_asns = override_attacker_asns
            branch = 0
        # Reuse the attacker from the last scenario for comparability
        elif (
            prev_attacker_asns
            and len(prev_attacker_asns) == self.scenario_config.num_attackers
        ):
            attacker_asns = prev_attacker_asns
            branch = 1
        # If old scenario has less attackers, get a superset of their attackers
        elif (
            prev_attacker_asns
            and len(prev_attacker_asns) < self.scenario_config.num_attackers
        ):
            branch = 2
            assert engine
            possible_attacker_asns = self._get_possible_attacker_asns(
                engine, self.percent_adoption
            )
            possible_attacker_asns = possible_attacker_asns.difference(
                prev_attacker_asns
            )

            assert len(possible_attacker_asns) >= (
                self.scenario_config.num_attackers - len(prev_attacker_asns)
            )
            # https://stackoverflow.com/a/15837796/8903959
            new_attacker_asns = frozenset(
                random.sample(
                    tuple(possible_attacker_asns),
                    self.scenario_config.num_attackers - len(prev_attacker_asns),
                )
            )
            attacker_asns = prev_attacker_asns | new_attacker_asns

        # This is being initialized for the first time
        else:
            branch = 3
            assert engine
            possible_attacker_asns = self._get_possible_attacker_asns(
                engine, self.percent_adoption
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
        prev_victim_asns: Optional[frozenset[int]],
        engine: Optional[BaseSimulationEngine],
        prev_scenario: Optional["Scenario"],
    ) -> frozenset[int]:
        """Returns victim ASN at random"""

        # This is coming from YAML, do not recalculate
        if override_victim_asns is not None:
            victim_asns = override_victim_asns
        # Reuse the victim from the last scenario for comparability
        elif (
            prev_victim_asns
            and len(prev_victim_asns) == self.scenario_config.num_victims
        ):
            victim_asns = prev_victim_asns
        # This is being initialized for the first time
        else:
            assert engine
            possible_victim_asns = self._get_possible_victim_asns(
                engine, self.percent_adoption
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

    def _get_adopting_asns(
        self,
        override_adopting_asns: Optional[frozenset[int]],
        adopting_asns: Optional[frozenset[int]],
        engine: Optional[BaseSimulationEngine],
    ) -> frozenset[int]:
        """Returns all asns that will be adopting self.AdoptPolicyCls"""

        if override_adopting_asns is not None:
            return override_adopting_asns
        # By default use the same adopting ASes as the last scenario config
        elif adopting_asns:
            return adopting_asns
        else:
            assert engine, "either yaml or engine must be set"
            adopting_asns = self._get_randomized_adopting_asns(engine)

        return adopting_asns

    def _get_randomized_adopting_asns(
        self,
        engine: BaseSimulationEngine,
    ) -> frozenset[int]:
        """Returns the set of adopting ASNs

        NOTE: this doesn't include ASNs listed in:
        hardcoded_asn_cls_dict
        default_adopters
        """

        adopting_asns: list[int] = list()
        # Randomly adopt in all three subcategories
        for subcategory in self.scenario_config.adoption_subcategory_attrs:
            asns = engine.as_graph.asn_groups[subcategory]
            # Remove ASes that are already pre-set
            # Ex: Attackers and victims, self.scenario_config.hardcoded_asn_cls_dict
            possible_adopters = asns.difference(self._preset_asns)

            # Get how many ASes should be adopting (store as k)
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

            try:
                # https://stackoverflow.com/a/15837796/8903959
                adopting_asns.extend(random.sample(tuple(possible_adopters), k))
            except ValueError:
                raise ValueError(f"{k} can't be sampled from {len(possible_adopters)}")
        return frozenset(adopting_asns)

    @cached_property
    def _default_adopters(self) -> frozenset[int]:
        """By default, victim always adopts"""

        return self.victim_asns

    @cached_property
    def _default_non_adopters(self) -> frozenset[int]:
        """By default, attacker always does not adopt"""

        return self.attacker_asns

    @cached_property
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

    def setup_engine(self, engine: BaseSimulationEngine) -> None:
        """Sets up engine"""

        # TODO: MOVE OUTSIDE OF THIS CLASS!!!!
        self.policy_classes_used = engine.setup(self)

    def get_policy_cls(self, as_obj: "AS") -> type[Policy]:
        """Returns the policy class for a given AS to set"""

        asn = as_obj.asn
        if self.AttackerBasePolicyCls and asn in self.attacker_asns:
            return self.AttackerBasePolicyCls
        elif asn in self._default_adopters:
            return self.AdoptPolicyCls
        elif Cls := self.scenario_config.hardcoded_asn_cls_dict.get(asn):
            return Cls
        elif asn in self.adopting_asns:
            return self.AdoptPolicyCls
        else:
            return self.BasePolicyCls

    ##################
    # Subclass Funcs #
    ##################

    @abstractmethod
    def _get_announcements(
        self,
        engine: Optional[BaseSimulationEngine] = None,
    ) -> tuple["Ann", ...]:
        """Returns announcements"""

        raise NotImplementedError

    def _get_roas(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional[BaseSimulationEngine] = None,
    ) -> tuple[ROA, ...]:
        """Returns a tuple of ROA's

        Not abstract and by default does nothing for
        backwards compatability
        """
        return ()

    def _add_roa_info_to_anns(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional[BaseSimulationEngine] = None,
    ) -> tuple["Ann", ...]:
        """Adds ROA Info to Announcements"""

        if self.roas:
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
        """Returns ROAChecker populated with self.roas"""

        roa_checker = ROAChecker()
        for roa in self.roas:
            roa_checker.insert(roa.prefix, roa)
        return roa_checker

    def _get_roa_origin(
        self, roa_checker: ROAChecker, prefix: IPv4Network | IPv6Network, origin: int
    ) -> Optional[int]:
        """Returns ROA origin"""

        roas = roa_checker.get_relevant_roas(prefix)
        if len(roas) == 0:
            return None
        elif len(roas) == 1:
            [roa] = roas
            return int(roa.origin)
        else:
            raise NotImplementedError

    def _get_roa_valid_length(
        self,
        roa_checker: ROAChecker,
        prefix: IPv4Network | IPv6Network,
        origin: int,
    ) -> Optional[bool]:
        """Returns ROA validity"""

        outcome = roa_checker.get_roa_outcome(prefix, origin)
        if outcome.validity in (
            ROAValidity.INVALID_LENGTH,
            ROAValidity.INVALID_LENGTH_AND_ORIGIN,
        ):
            return False
        elif outcome.validity == ROAValidity.UNKNOWN:
            return None
        elif outcome.validity in (ROAValidity.VALID, ROAValidity.INVALID_ORIGIN):
            return True
        else:
            raise NotImplementedError(f"Should never reach this {outcome.validity}")

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
        # Add ROA prefixes here, so that if we blackhole a non routed
        # prefix of a superprefix hijack this won't break
        # (since the prefix would only exist in the ROA)
        for roa in self.roas:
            prefixes.add(str(roa.prefix))
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

    ##############
    # Yaml Funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[Any, Any]:
        """This optional method is called when you call yaml.dump()"""

        config_to_save = replace(
            self.scenario_config,
            override_attacker_asns=self.attacker_asns,
            override_victim_asns=self.victim_asns,
            override_adopting_asns=self.adopting_asns,
            override_announcements=self.announcements,
        )

        return {
            "scenario_config": config_to_save,
            "percent_adoption": self.percent_adoption,
        }

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """This optional method is called when you call yaml.load()"""

        return cls(
            scenario_config=dct["scenario_config"],
            percent_adoption=dct["percent_adoption"],
        )
