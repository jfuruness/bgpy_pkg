import random

from lib_caida_collector import AS

from yamlable import YamlAble, yaml_info, yaml_info_decorate

from ipaddress import ip_network

from ..announcements import Announcement
from ..enums import Outcomes, Relationships


@yaml_info(yaml_tag="EngineInput")
class EngineInput(YamlAble):
    """Contains information regarding an attack"""

    __slots__ = ("attacker_asn", "victim_asn", "adopting_asns",
                 "announcements", "as_classes", "extra_ann_kwargs",
                 "prefix_subprefix_dict")

    # This is the base type of announcement for this class
    # You can subclass this engine input and specify a different base ann
    AnnCls = Announcement

    y_labels = {Outcomes.ATTACKER_SUCCESS: "Percent Attacker Success",
                Outcomes.VICTIM_SUCCESS: "Percent Legitimate Origin Success",
                Outcomes.DISCONNECTED: "Percent Disconnected"}

    subclasses = []

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to know all attackers that have been created
        """

        super().__init_subclass__(*args, **kwargs)
        # Add yaml tag to subclass
        yaml_info_decorate(cls, yaml_tag=cls.__name__)

    def __init__(self,
                 subgraph_asns=None,
                 engine=None,
                 percent_adopt=None,
                 # These are normally set to None
                 attacker_asn=None,
                 victim_asn=None,
                 as_classes=None,
                 **extra_ann_kwargs):
        """Inits engine input, determines adopters, regens from yaml

        subgraph_asns: a dict of asns, can be useful for determining adopters
        engine: The simulator engine
        percent_adopt: The percent adoption
        
        Yaml attrs (only used when regenerating from yaml)
        attacker_asn: ASN of the attacker
        victim_asn: ASN of the victim
        as_classes: Dict of asn: ASCls. Non listed ASNs default to BGP
        """

        # If regenerating from yaml, save attacker asn
        if attacker_asn:
            self.attacker_asn = attacker_asn
        # Otherwise randomly select the attacker asn
        else:
            self.attacker_asn = self._get_attacker_asn(subgraph_asns, engine)

        # If regenerating from yaml, save the victim asn
        if victim_asn:
            self.victim_asn = victim_asn
        # Otherwise rndomly select the victim asn
        else:
            self.victim_asn = self._get_victim_asn(subgraph_asns, engine)

        # If regenerating from yaml
        if as_classes:
            # Set adopting ASNs to None and save the as_classes
            self.adopting_asns = None
            self.as_classes = as_classes
        else:
            # Get the adopting asns randomly
            self.adopting_asns = self._get_adopting_asns(subgraph_asns,
                                                         engine,
                                                         percent_adopt)
            self.as_classes = None
        # Used for dumping and loading yaml
        self.extra_ann_kwargs = extra_ann_kwargs
        # Generate announcements now that you have attacker+victim
        self.announcements = self._get_announcements(**extra_ann_kwargs)
        # Announcement prefixes must overlap
        # If they don't, traceback wouldn't work
        first_prefix = ip_network(self.announcements[0].prefix)
        for ann in self.announcements:
            assert ip_network(ann.prefix).overlaps(first_prefix)
        self._get_prefix_subprefix_dict()

    def seed(self, engine, *args):
        """Seeds announcement at the proper AS

        Since this is the simulator engine, we should
        never have to worry about overlapping announcements
        """

        for ann in self.announcements:
            obj_to_seed = engine.as_dict[ann.seed_asn]
            err = "Seeding conflict"
            assert obj_to_seed._local_rib.get_ann(ann.prefix) is None, err

            obj_to_seed._local_rib.add_ann(ann)

    def determine_outcome(self, as_obj, ann):
        """Determines outcome of traceback

        as_obj is the AS passed in, ann is the most specific prefix ann

        This assumes that the as_obj is the last in the path
        """

        # If the AS obj is the attacker, we have reached the attacker
        # Therefore the attacker has won
        if self.attacker_asn == as_obj.asn:
            return Outcomes.ATTACKER_SUCCESS
        # If the AS Obj is the victim, the victim has won
        elif self.victim_asn == as_obj.asn:
            return Outcomes.VICTIM_SUCCESS
        # End of traceback. Didn't reach atk/vic so it's disconnected
        # Note that there is no good way to end, which is why we have
        # The traceback_end just in case
        # Since paths could be lies, and for things like blackholes
        # The recv relationship must not be the origin
        elif (ann is None or
              len(ann.as_path) == 1
              or ann.recv_relationship == Relationships.ORIGIN
              or ann.traceback_end):

            return Outcomes.DISCONNECTED
        # Keep going - we have not yet reached the end of the as path
        else:
            return None

    def post_propagation_hook(self, *args, **kwargs):
        """Function called after propagation

        Useful for subclasses that need to modify the simulator
        post propagation in some manner
        """

        pass

##############################
# Select Attacker and victim #
##############################

    def _get_attacker_asn(self, subgraphs, engine):
        """Returns attacker ASN at random"""

        possible_attacker_asns = self._possible_attackers(subgraphs, engine)
        return random.choice(tuple(possible_attacker_asns))

    def _possible_attackers(self, subgraph_asns, engine):
        """By default, only stubs_and_mh ases can attack"""

        return subgraph_asns["stubs_and_mh"]

    def _get_victim_asn(self, subgraph_asns, engine):
        """Returns victim ASN at random. Attacker can't be victim"""


        possible_vic_asns = self._possible_victims(subgraph_asns, engine)
        return random.choice(tuple(
            possible_vic_asns.difference([self.attacker_asn])))

    def _possible_victims(self, subgraph_asns, engine):
        """By default, only stubs or mh ASes can be victims"""

        return subgraph_asns["stubs_and_mh"]

#######################
# Adopting ASNs funcs #
#######################

    def _get_adopting_asns(self, subgraph_asns, engine, percent_adopt):
        """Get adopting ASNs"""

        adopting_asns = list()
        for asns in subgraph_asns.values():
            # Remove uncountable ASes such as victim and attacker
            possible_adopters = asns.difference(self.uncountable_asns)
            # Get how many ASes should be adopting
            k = len(possible_adopters) * percent_adopt // 100
            # Round for the start and end of the graph
            # (if 0 ASes would be adopting, have 1 as adopt)
            # (If all ASes would be adopting, have all -1 adopt)
            # This feature was chosen by my professors
            if k == 0:
                k += 1
            elif k == len(possible_adopters):
                k -= 1

            adopting_asns.extend(random.sample(possible_adopters, k))
        adopting_asns += self._default_adopters()
        assert len(adopting_asns) == len(set(adopting_asns))
        return adopting_asns

    def _default_adopters(self):
        """By default, victim always adopts"""

        return [self.victim_asn]

    def _default_non_adopters(self):
        """By default, attacker always does not adopt"""

        return [self.attacker_asn]

    @property
    def uncountable_asns(self):
        """ASNs that we do not count for statistics since they are defaults"""

        return self._default_adopters() + self._default_non_adopters()

    def get_as_classes(self, engine, BaseASCls, AdoptingASCls):
        """Returns dict of asn: ASCls. If not specified, asn is BGP"""

        if self.as_classes:
            return self.as_classes
        else:
            return {asn: AdoptingASCls for asn in self.adopting_asns}

################
# Helper Funcs #
################

    def _get_prefix_subprefix_dict(self):
        """Saves a dict of prefix to subprefixes"""

        prefixes = set([])
        for ann in self.announcements:
            prefixes.add(ann.prefix)
        # Do this here for speed
        prefixes = [ip_network(x) for x in prefixes]

        prefix_subprefix_dict = {x: [] for x in prefixes}
        for outer_prefix, subprefix_list in prefix_subprefix_dict.items():
            for prefix in prefixes:
                if prefix.subnet_of(outer_prefix) and prefix != outer_prefix:
                    subprefix_list.append(str(prefix))
        # Get rid of ip_network
        self.prefix_subprefix_dict = {str(k): v for k, v
                                      in prefix_subprefix_dict.items()}

##############
# Yaml Funcs #
##############

    def __to_yaml_dict__(self):
        """This optional method is called when you call yaml.dump()"""
        return {"attacker_asn": self.attacker_asn,
                "victim_asn": self.victim_asn,
                "as_classes": {asn: AS.subclass_to_name_dict[ASCls]
                               for asn, ASCls in self.as_classes.items()},
                "extra_ann_kwargs": self.extra_ann_kwargs}

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """This optional method is called when you call yaml.load()"""
        as_classes = {asn: AS.name_to_subclass_dict[name]
                      for asn, name in dct["as_classes"].items()}

        return cls(attacker_asn=dct["attacker_asn"],
                   victim_asn=dct["victim_asn"],
                   as_classes=as_classes,
                   **dct["extra_ann_kwargs"])
