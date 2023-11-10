from abc import ABC, abstractmethod
from dataclasses import replace
import math
import random
from ipaddress import ip_network
from ipaddress import IPv4Network
from ipaddress import IPv6Network
from typing import Any, Optional, Type, Union
import warnings

from frozendict import frozendict

from bgpy.caida_collector import AS

from .scenario_config import ScenarioConfig

from bgpy.simulation_engine import Announcement
from bgpy.simulation_engine import SimulationEngine
from bgpy.enums import SpecialPercentAdoptions, Outcomes, Relationships

pseudo_base_cls_dict: dict[type[AS], type[AS]] = dict()


class Scenario(ABC):
    """Contains information regarding a scenario/attack

    This represents a single trial
    """

    def __init__(
        self,
        *,
        scenario_config: ScenarioConfig,
        percent_adoption: Union[float, SpecialPercentAdoptions] = 0,
        engine: Optional[SimulationEngine] = None,
        prev_scenario: Optional["Scenario"] = None,
    ):
        """inits attrs

        Any kwarg prefixed with default is only required for the test suite/YAML
        """

        self.scenario_config: ScenarioConfig = scenario_config
        self.percent_adoption: Union[float, SpecialPercentAdoptions] = percent_adoption

        self.attacker_asns: frozenset[int] = self._get_attacker_asns(
            scenario_config.override_attacker_asns, engine, prev_scenario
        )

        self.victim_asns: frozenset[int] = self._get_victim_asns(
            scenario_config.override_victim_asns, engine, prev_scenario
        )

        AS_CLS_DCT = dict[int, type[AS]]
        self.non_default_asn_cls_dict: AS_CLS_DCT = self._get_non_default_asn_cls_dict(
            scenario_config.override_non_default_asn_cls_dict, engine, prev_scenario
        )

        if self.scenario_config.override_announcements:
            self.announcements: tuple[
                "Announcement", ...
            ] = self.scenario_config.override_announcements
        else:
            self.announcements = self._get_announcements(
                engine=engine, prev_scenario=prev_scenario
            )

        self.ordered_prefix_subprefix_dict: dict[
            str, list[str]
        ] = self._get_ordered_prefix_subprefix_dict()

        self.as_classes_used: frozenset[Type[AS]] = frozenset()

    #################
    # Get attackers #
    #################

    def _get_attacker_asns(
        self,
        override_attacker_asns: Optional[frozenset[int]],
        engine: Optional[SimulationEngine],
        prev_scenario: Optional["Scenario"],
    ) -> frozenset[int]:
        """Returns attacker ASN at random"""

        # This is coming from YAML, do not recalculate
        if override_attacker_asns:
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
        engine: SimulationEngine,
        percent_adoption: Union[float, SpecialPercentAdoptions],
        prev_scenario: Optional["Scenario"],
    ) -> set[int]:
        """Returns possible attacker ASNs, defaulted from config"""

        possible_asns = engine.asn_groups[
            self.scenario_config.attacker_subcategory_attr
        ]
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, set), err
        return possible_asns

    ###############
    # Get Victims #
    ###############

    def _get_victim_asns(
        self,
        override_victim_asns: Optional[frozenset[int]],
        engine: Optional[SimulationEngine],
        prev_scenario: Optional["Scenario"],
    ) -> frozenset[int]:
        """Returns victim ASN at random"""

        # This is coming from YAML, do not recalculate
        if override_victim_asns:
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
        engine: SimulationEngine,
        percent_adoption: Union[float, SpecialPercentAdoptions],
        prev_scenario: Optional["Scenario"],
    ) -> set[int]:
        """Returns possible victim ASNs, defaulted from config"""

        possible_asns = engine.asn_groups[self.scenario_config.victim_subcategory_attr]
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, set), err
        # Remove attackers from possible victims
        possible_asns = possible_asns.difference(self.attacker_asns)
        return possible_asns

    #######################
    # Adopting ASNs funcs #
    #######################

    def _get_non_default_asn_cls_dict(
        self,
        override_non_default_asn_cls_dict: Union[
            Optional[frozendict[int, type[AS]]],
            # Must include due to mypy weirdness
            # about empty frozendicts
            frozendict[str, None],
        ],
        engine: Optional[SimulationEngine],
        prev_scenario: Optional["Scenario"],
    ) -> dict[int, type[AS]]:
        """Returns as class dict

        non_default_asn_cls_dict is a dict of asn: AdoptASCls
        where you do __not__ include any of the BaseASCls,
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
            for asn, OldASCls in prev_scenario.non_default_asn_cls_dict.items():
                HardcodedCls = self.scenario_config.hardcoded_asn_cls_dict.get(asn)
                if HardcodedCls:
                    non_default_asn_cls_dict[asn] = HardcodedCls
                # If the ASN was of the adopting class of the last scenario,
                # Update the adopting AS class for the new scenario
                elif OldASCls == prev_scenario.scenario_config.AdoptASCls:
                    non_default_asn_cls_dict[asn] = self.scenario_config.AdoptASCls
                # # Otherwise keep the AS class as it was
                # # This is useful for things like ROV, etc...
                # else:
                #     non_default_asn_cls_dict[asn] = OldASCls
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
        for asn, ASCls in non_default_asn_cls_dict.items():
            assert ASCls != self.scenario_config.BaseASCls, "No defaults!"

        return non_default_asn_cls_dict

    def _get_randomized_non_default_asn_cls_dict(
        self,
        engine: SimulationEngine,
    ) -> dict[int, type[AS]]:
        """Get adopting ASNs and non default ASNs

        By default, to get even adoption, adopt in each of the three
        subcategories
        """

        # Get the asn_cls_dict without randomized adoption
        asn_cls_dict = dict(self.scenario_config.hardcoded_asn_cls_dict)
        for asn in self._default_adopters:
            asn_cls_dict[asn] = self.scenario_config.AdoptASCls

        # Randomly adopt in all three subcategories
        for subcategory in self.scenario_config.adoption_subcategory_attrs:
            asns = engine.asn_groups[subcategory]
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
                    asn_cls_dict[asn] = self.scenario_config.AdoptASCls
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

    #############################
    # Engine Manipulation Funcs #
    #############################

    def setup_engine(
        self, engine: SimulationEngine, prev_scenario: Optional["Scenario"] = None
    ) -> None:
        """sets up engine input"""

        self._set_engine_as_classes(engine, prev_scenario)
        self._seed_engine_announcements(engine, prev_scenario)
        engine.ready_to_run_round = 0

    def _set_engine_as_classes(
        self, engine: SimulationEngine, prev_scenario: Optional["Scenario"]
    ) -> None:
        """Resets Engine ASes and changes their AS class

        We do this here because we already seed from the scenario
        to allow for easy overriding. If scenario controls seeding,
        it doesn't make sense for engine to control resetting either
        and have each do half and half
        """

        as_classes_used = set()
        # Done here to save as much time  as possible
        BaseASCls = self.scenario_config.BaseASCls
        for as_obj in engine:
            # set the AS class to be the proper type of AS
            cls = self.non_default_asn_cls_dict.get(as_obj.asn, BaseASCls)
            as_obj.__class__ = cls
            as_classes_used.add(cls)
            # Clears all RIBs, etc
            # Reset base is False to avoid overrides base AS info (peers, etc)
            as_obj.__init__(reset_base=False)
        self.as_classes_used = frozenset(as_classes_used)

    def _seed_engine_announcements(
        self, engine: SimulationEngine, prev_scenario: Optional["Scenario"]
    ) -> None:
        """Seeds announcement at the proper AS

        Since this is the simulator engine, we should
        never have to worry about overlapping announcements
        """

        for ann in self.announcements:
            assert ann.seed_asn is not None
            # Get the AS object to seed at
            # Must ignore type because it doesn't see assert above
            obj_to_seed = engine.as_dict[ann.seed_asn]  # type: ignore
            # Ensure we aren't replacing anything
            err = "Seeding conflict"
            assert obj_to_seed._local_rib.get_ann(ann.prefix) is None, err
            # Seed by placing in the local rib
            obj_to_seed._local_rib.add_ann(ann)

    ##################
    # Subclass Funcs #
    ##################

    @abstractmethod
    def _get_announcements(self, *args, **kwargs):
        """Returns announcements"""

        raise NotImplementedError

    def pre_aggregation_hook(self, *args, **kwargs):
        """Useful hook for changes/checks
        prior to results aggregation.
        """
        pass

    def post_propagation_hook(self, *args, **kwargs):
        """Useful hook for post propagation"""

        pass

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
            f"{self.scenario_config.BaseASCls.name} "
            "({self.scenario_config.AdoptASCls.name} adopting)"
        )

    ##############
    # Yaml Funcs #
    ##############

    @property
    def _yamlable_non_default_asn_cls_dict(self) -> dict[int, str]:
        """Converts non default as cls dict to a yamlable dict of asn: name"""

        return {
            asn: AS.subclass_to_name_dict[ASCls]
            for asn, ASCls in self.non_default_asn_cls_dict.items()
        }

    @staticmethod
    def _get_non_default_asn_cls_dict_from_yaml(yaml_dict) -> dict[int, type[AS]]:
        """Converts yamlified non_default_asn_cls_dict back to normal asn: class"""

        return {asn: AS.name_to_subclass_dict[name] for asn, name in yaml_dict.items()}

    def __to_yaml_dict__(self) -> dict[Any, Any]:
        """This optional method is called when you call yaml.dump()"""

        config_to_save = replace(
            self.scenario_config,
            override_attacker_asns=self.attacker_asns,
            override_victim_asns=self.victim_asns,
            override_non_default_as_cls_dict=self._yamlable_non_default_asn_cls_dict,
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

    ####################
    # Deprecated funcs #
    ####################

    def determine_as_outcome(self, as_obj: AS, ann: Optional[Announcement]) -> Outcomes:
        """Determines the outcome at an AS

        ann is most_specific_ann is the most specific prefix announcement
        that exists at that AS
        """

        warnings.warn(
            "Deprecated, untested, please don't use. Leaving this until 2025"
            " so that a few PhD students can graduate :)",
            DeprecationWarning,
        )

        if as_obj.asn in self.attacker_asns:
            return Outcomes.ATTACKER_SUCCESS
        elif as_obj.asn in self.victim_asns:
            return Outcomes.VICTIM_SUCCESS
        # End of traceback
        elif (
            ann is None
            or len(ann.as_path) == 1
            or ann.recv_relationship == Relationships.ORIGIN
            or ann.traceback_end
        ):
            return Outcomes.DISCONNECTED
        else:
            return Outcomes.UNDETERMINED

    @property
    def graph_label(self) -> str:
        """Label that will be used on the graph"""

        warnings.warn(
            "Deprecated, untested, please don't use. Leaving this until 2025"
            " so that a few PhD students can graduate :)",
            DeprecationWarning,
        )

        if self.scenario_config.scenario_label:
            return self.scenario_config.scenario_label
        elif self.scenario_config.AdoptASCls:
            return (
                f"{self.scenario_config.BaseASCls.name} "
                f"({self.scenario_config.AdoptASCls.name} adopting)"
            )
        else:
            return f"{self.scenario_config.BaseASCls.name} (None adopting)"
