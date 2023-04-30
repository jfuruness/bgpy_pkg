from abc import ABC, abstractmethod
import math
import random
from ipaddress import ip_network
from ipaddress import IPv4Network
from ipaddress import IPv6Network
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union
from warnings import warn

from caida_collector_pkg import AS

from ...enums import Outcomes
from ...enums import Relationships
from ...enums import SpecialPercentAdoptions
from ...simulation_engine import Announcement
from ...simulation_engine import BGPSimpleAS
from ...simulation_engine import RealROVSimpleAS
from ...simulation_engine import SimulationEngine

pseudo_base_cls_dict: Dict[Type[AS], Type[AS]] = dict()


class ScenarioTrial(ABC):
    """Contains information regarding a scenario/attack

    This represents a single trial
    """

    def __init__(
        self,
        *,
        scenario_config: ScenarioConfig
        engine: SimulationEngine,
        percent_adoption: Union[float, SpecialPercentAdoptions],
        prev_scenario: Optional[ScenarioTrial] = None,
        # Only necessary if coming from YAML
        yaml_attacker_asns: Optional[Set[int]] = None,
        yaml_victim_asns: Optional[Set[int]] = None,
        yaml_non_default_asn_cls_dict: Optional[Dict[int, Type[AS]]] = None,
        yaml_announcements: Tuple[Announcement, ...] = (),
    ):
        """inits attrs

        non_base_as_cls_dict is a dict of asn: ASCls
        where you do __not__ include any of the BaseASCls,
        since that is the default
        """

        self.scenario_config: ScenarioConfig = scenario_config
        self.percent_adoption: Union[float, SpecialPercentAdoptions] = percent_adoption

        self.attacker_asns: Set[int] = self._get_attacker_asns(
            yaml_attacker_asns,
            engine,
            prev_scenario
        )

        self.victim_asns: Set[int] = self._get_victim_asns(
            yaml_victim_asns,
            engine,
            prev_scenario
        )

        AS_CLS_DCT = Dict[int, Type[AS]]
        self.non_default_asn_cls_dict: AS_CLS_DCT = self._get_non_default_asn_cls_dict(
            yaml_non_default_asn_cls_dict,
            engine,
            prev_scenario
        )

        raise NotImplementedError
        if announcements:
            self.announcements: Tuple["Announcement", ...] = announcements

    #################
    # Get attackers #
    #################

    def _get_attacker_asns(
        self,
        yaml_attacker_asns: Set[int],
        engine: SimulationEngine,
        prev_scenario: Optional["Scenario"]
    ) -> Set[int]:
        """Returns attacker ASN at random"""

        # This is coming from YAML, do not recalculate
        if yaml_attacker_asns:
            attacker_asns = yaml_attacker_asns
        # Reuse the attacker from the last scenario for comparability
        elif prev_scenario:
            attacker_asns = prev_scenario.attacker_asns
        # This is being initialized for the first time
        else:
            possible_attacker_asns = self._get_possible_attacker_asns(
                engine,
                self.percent_adoption,
                prev_scenario
            )
            # https://stackoverflow.com/a/15837796/8903959
            attacker_asns = set(
                random.sample(
                    tuple(possible_attacker_asns),
                    self.scenario_config.num_attackers
                )
            )

        # Validate attacker asns
        err = "Number of attackers is different from attacker length"
        assert len(attacker_asns) == num_attackers, err

        return attacker_asns

    def _get_possible_attacker_asns(
        self,
        engine: SimulationEngine,
        percent_adoption: Union[float, SpecialPercentAdoptions],
        prev_scenario: Optional["Scenario"]
    ) -> Set[int]:
        """Returns possible attacker ASNs, defaulted from config"""

        possible_asns = getattr(engine, self.scenario_config.attacker_subcategory_attr)
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, set), err
        return possible_asns

    ###############
    # Get Victims #
    ###############

    def _get_victim_asns(
        self,
        yaml_victim_asns: Set[int],
        engine: SimulationEngine,
        prev_scenario: Optional["Scenario"]
    ) -> Set[int]:
        """Returns victim ASN at random"""

        # This is coming from YAML, do not recalculate
        if yaml_victim_asns:
            victim_asns = yaml_victim_asns
        # Reuse the victim from the last scenario for comparability
        elif prev_scenario:
            victim_asns = prev_scenario.victim_asns
        # This is being initialized for the first time
        else:
            possible_victim_asns = self._get_possible_victim_asns(
                engine,
                self.percent_adoption,
                prev_scenario
            )
            # https://stackoverflow.com/a/15837796/8903959
            victim_asns = set(
                random.sample(
                    tuple(possible_victim_asns),
                    self.scenario_config.num_victims
                )
            )

        err = "Number of victims is different from victim length"
        assert len(victim_asns) == num_victims, err

        return victim_asns

    def _get_possible_victim_asns(
        self,
        engine: SimulationEngine,
        percent_adoption: Union[float, SpecialPercentAdoptions],
        prev_scenario: Optional["Scenario"]
    ) -> Set[int]:
        """Returns possible victim ASNs, defaulted from config"""

        possible_asns = getattr(engine, self.scenario_config.victim_subcategory_attr)
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
        yaml_non_default_asn_cls_dict: Dict[int, Type[AS]],
        engine: SimulationEngine,
        prev_scenario: Optional["Scenario"]
    ) -> Dict[int, Type[AS]]:
        """Returns as class dict

        non_default_as_cls_dict is a dict of asn: AdoptASCls
        where you do __not__ include any of the BaseASCls,
        since that is the default

        By default, we use the previous engine input to maintain static
        adoption across trials
        """

        if yaml_non_default_asn_cls_dict:
            return yaml_non_default_asn_cls_dict
        # By default, use the last engine input to maintain static
        # adoption across the graph
        elif prev_scenario:
            non_default_as_cls_dict = dict()
            for asn, OldASCls in prev_scenario.non_default_as_cls_dict.items():
                # If the ASN was of the adopting class of the last scenario,
                # Update the adopting AS class for the new scenario
                if OldASCls == prev_scenario.AdoptASCls:
                    non_default_as_cls_dict[asn] = self.AdoptASCls
                # Otherwise keep the AS class as it was
                # This is useful for things like ROV, etc...
                else:
                    non_default_as_cls_dict[asn] = OldASCls
            return non_default_as_cls_dict
        # Randomly get adopting ases if it hasn't been set yet
        else:
            return self._get_randomized_non_default_asn_cls_dict(engine)

    def _get_randomized_non_default_asn_cls_dict(
        self,
        engine: SimulationEngine,
    ) -> Dict[int, Type[AS]]:
        """Get adopting ASNs and non default ASNs

        By default, to get even adoption, adopt in each of the three
        subcategories
        """

        # Get the asn_cls_dict without randomized adoption
        asn_cls_dict = self.scenario_config.hardcoded_asn_cls_dict.copy()
        for asn in self._default_adopters:
            asn_cls_dict[asn] = self.AdoptASCls

        # Randomly adopt in all three subcategories
        for subcategory in self.scenario_config.adoption_subcategory_attrs:
            asns = getattr(engine, subcategory)
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
            else:
                assert isinstance(self.percent_adoption, float), "Make mypy happy"
                k = math.ceil(len(possible_adopters) * self.percent_adoption)

            # https://stackoverflow.com/a/15837796/8903959
            possible_adopters = tuple(possible_adopters)
            try:
                for asn in random.sample(possible_adopters, k):
                    asn_cls_dict[asn] = self.AdoptASCls
            except ValueError:
                raise ValueError(
                    f"{k} can't be sampled from {len(possible_adopters)}")
        return asn_cls_dict

    @property
    def _default_adopters(self) -> Set[int]:
        """By default, victim always adopts"""

        return self.victim_asns

    @property
    def _default_non_adopters(self) -> Set[int]:
        """By default, attacker always does not adopt"""

        return self.attacker_asns

    @property
    def _preset_asns(self) -> Set[int]:
        """ASNs that have a preset adoption policy"""

        # Returns the union of default adopters and non adopters
        hardcoded_asns = set(self.scenario_config.hardcoded_asn_cls_dict)
        return self._default_adopters | self._default_non_adopters | hardcoded_asns

    ##############################################
    # Set Attacker/Victim and Announcement Funcs #
    ##############################################


raise NotImplementedError


    def _get_announcements(
        self,
        engine: SimulationEngine,
        prev_scenario: Optional["Scenario"]
    ):
        """Returns announcements"""

        # Must call this here due to atk/vic pair being different
        self.announcements = self._get_announcements(
            engine=engine,
            percent_adoption=percent_adoption,
            prev_scenario=prev_scenario)
        self._get_ordered_prefix_subprefix_dict()

    @abstractmethod
    def _get_announcements(self, *args, **kwargs):
        """Returns announcements"""

        raise NotImplementedError


    def determine_as_outcome(self,
                             as_obj: AS,
                             ann: Optional[Announcement]
                             ) -> Outcomes:
        """Determines the outcome at an AS

        ann is most_specific_ann is the most specific prefix announcement
        that exists at that AS
        """

        if as_obj.asn in self.attacker_asns:
            return Outcomes.ATTACKER_SUCCESS
        elif as_obj.asn in self.victim_asns:
            return Outcomes.VICTIM_SUCCESS
        # End of traceback
        elif (ann is None
              or len(ann.as_path) == 1
              or ann.recv_relationship == Relationships.ORIGIN
              or ann.traceback_end):
            return Outcomes.DISCONNECTED
        else:
            return Outcomes.UNDETERMINED

    def determine_as_outcome_ctrl_plane(self,
                                        as_obj: AS,
                                        ann: Optional[Announcement]
                                        ) -> Outcomes:
        """Determines the outcome at an AS on the control plane

        ann is most_specific_ann is the most specific prefix announcement
        that exists at that AS
        """

        if not ann:
            return Outcomes.DISCONNECTED
        elif ann.origin in self.attacker_asns:
            return Outcomes.ATTACKER_SUCCESS
        elif ann.origin in self.victim_asns:
            return Outcomes.VICTIM_SUCCESS
        else:
            return Outcomes.DISCONNECTED

    #############################
    # Engine Manipulation Funcs #
    #############################

    def setup_engine(self,
                     engine: SimulationEngine,
                     percent_adoption: Union[float, SpecialPercentAdoptions],
                     prev_scenario: Optional["Scenario"] = None):
        """Sets up engine input"""

        self._set_attackers_victims_anns(engine,
                                         percent_adoption,
                                         prev_scenario)
        self._set_engine_as_classes(engine, percent_adoption, prev_scenario)
        self._seed_engine_announcements(engine,
                                        percent_adoption,
                                        prev_scenario)
        engine.ready_to_run_round = 0

    def _set_engine_as_classes(
            self,
            engine: SimulationEngine,
            percent_adoption: Union[float, SpecialPercentAdoptions],
            prev_scenario: Optional["Scenario"]):
        """Resets Engine ASes and changes their AS class

        We do this here because we already seed from the scenario
        to allow for easy overriding. If scenario controls seeding,
        it doesn't make sense for engine to control resetting either
        and have each do half and half
        """

        raise NotImplementedError("MUST keep track of both adopting asn cls dict"
            "AND hardcoded asn cls dict!!!")
        # non_default_as_cls_dict is a dict of asn: AdoptASCls
        # where you do __not__ include any of the BaseASCls,
        # since that is the default
        # Only regenerate this if it's not already set (like with YAML)
        self.non_default_as_cls_dict = self._get_non_default_as_cls_dict(
            engine,
            percent_adoption,
            prev_scenario=prev_scenario)
        # Validate that this is only non_default ASes
        # This matters, because later this entire dict may be used for the next
        # scenario
        for asn, ASCls in self.non_default_as_cls_dict.items():
            assert ASCls != self.BaseASCls, "No defaults! See comment above"

        # Done here to save as much time  as possible
        BaseASCls = self.BaseASCls
        for as_obj in engine:
            # Set the AS class to be the proper type of AS
            as_obj.__class__ = self.non_default_as_cls_dict.get(as_obj.asn,
                                                                BaseASCls)
            # Clears all RIBs, etc
            # Reset base is False to avoid overrides base AS info (peers, etc)
            as_obj.__init__(reset_base=False)

    def _seed_engine_announcements(self, engine: SimulationEngine, *args):
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

    def pre_aggregation_hook(self, *args, **kwargs):
        """ Useful hook for changes/checks
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
        prefixes: List[Union[IPv4Network, IPv6Network]] = [  # type: ignore
            ip_network(x) for x in prefixes]
        # Sort prefixes with most specific prefix first
        # Note that this must be sorted for the traceback to get the
        # most specific prefix first
        prefixes = list(sorted(prefixes,
                               key=lambda x: x.num_addresses))  # type: ignore

        prefix_subprefix_dict = {x: [] for x in prefixes}  # type: ignore
        for outer_prefix, subprefix_list in prefix_subprefix_dict.items():
            for prefix in prefixes:
                if (prefix.subnet_of(outer_prefix)  # type: ignore
                        and prefix != outer_prefix):
                    subprefix_list.append(str(prefix))
        # Get rid of ip_network
        self.ordered_prefix_subprefix_dict: Dict[str, List[str]] = {
            str(k): v for k, v in prefix_subprefix_dict.items()}

    ##############
    # Yaml Funcs #
    ##############

    def __to_yaml_dict__(self) -> Dict[Any, Any]:
        """This optional method is called when you call yaml.dump()"""

        return {"announcements": self.announcements,
                "attacker_asns": self.attacker_asns,
                "victim_asns": self.victim_asns,
                "num_victims": self.num_victims,
                "num_attackers": self.num_attackers,
                "min_rov_confidence": self.min_rov_confidence,
                "adoption_subcategory_attrs": self.adoption_subcategory_attrs,
                "non_default_as_cls_dict":
                    {asn: AS.subclass_to_name_dict[ASCls]
                     for asn, ASCls in self.non_default_as_cls_dict.items()}}

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """This optional method is called when you call yaml.load()"""

        as_classes = {asn: AS.name_to_subclass_dict[name]
                      for asn, name in dct["non_default_as_cls_dict"].items()}

        return cls(announcements=dct["announcements"],
                   attacker_asns=dct["attacker_asns"],
                   victim_asns=dct["victim_asns"],
                   num_victims=dct["num_victims"],
                   num_attackers=dct["num_attackers"],
                   min_rov_confidence=dct["min_rov_confidence"],
                   non_default_as_cls_dict=as_classes,
                   adoption_subcategory_attrs=dct["adoption_subcategory_attrs"]
                   )
