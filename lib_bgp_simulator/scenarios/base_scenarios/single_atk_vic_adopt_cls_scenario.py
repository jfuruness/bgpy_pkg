import random

from lib_caida_collector import AS

from yamlable import YamlAble, yaml_info, yaml_info_decorate

from ipaddress import ip_network

from ..announcements import Announcement
from ..enums import Outcomes, Relationships


@yaml_info(yaml_tag="SingleAtkVicAdoptClsScenario")
class SingleAtkVicAdoptClsScenario(Scenario):
    """Contains information regarding an attack

    This scenario has a single attacker and victim pair,
    as well as a single adopting AS Class
    """

    __slots__ = ("attacker_asn", "victim_asn")


    def __init__(self,
                 *args,
                 AdoptASCls=None,
                 attacker_asn=None,
                 victim_asn=None,
                 **kwargs):

        assert AdoptASCls

        # If we are regenerating from yaml
        self.attacker_asn = attacker_asn
        self.victim_asn = victim_asn

        self.AdoptASCls = AdoptASCls

        super(SingleAtkVicAdoptClsScenario, self).__init__(*args, **kwargs)

    def setup_engine(self, *args, **kwargs):
        """Sets up engine input"""

        self._set_attacker_victim_pair(*args, **kwargs)

        super(SingleAtkVicAdoptClsScenario, self).setup_engine(*args, **kwargs)

    def unique_graph_label(self):
        """Returns unique graph label that no other scenario has"""

        return f"{self.AdoptASCls.name} Adopting"

    def post_propagation_hook(self, engine, data_point):
        """Useful hook for post propagation"""

        pass

##################
# Abstract Funcs #
##################

    @property
    @abstractmethod
    def _get_announcements(self):
        """Returns announcements"""

        raise NotImplementedError

##############################
# Select Attacker and victim #
##############################

    def _set_attacker_victim_pair(self, *args, **kwargs):
        """Sets attacker victim pair"""

        self.attacker_asn = self._get_attacker_asn(*args, **kwargs)
        self.victim_asn = self._get_victim_asn(*args, **kwargs)

    def _get_attacker_asn(self, *args, **kwargs):
        """Returns attacker ASN at random"""

        possible_attacker_asns = self._get_possible_attackers(*args, **kwargs)
        return random.choice(tuple(possible_attacker_asns))

    def _get_victim_asn(self, subgraph_asns, engine):
        """Returns victim ASN at random. Attacker can't be victim"""


        possible_vic_asns = self._get_possible_victims(*args, **kwargs)
        return random.choice(tuple(
            possible_vic_asns.difference([self.attacker_asn])))

    # For this, don't bother making a subclass with stubs_and_mh
    # Since it won't really create another class branch,
    # Since another dev would likely just subclass from the same place
    def _get_possible_attacker_asns(self, engine, percent_adoption):
        """Returns possible attacker ASNs, defaulted from stubs_and_mh"""

        return set([x.asn for x in engine.stubs_and_mh])

    # For this, don't bother making a subclass with stubs_and_mh
    # Since it won't really create another class branch,
    # Since another dev would likely just subclass from the same place
    def _get_possible_victim_asns(self, engine, percent_adoption):
        """Returns possible victim ASNs, defaulted from stubs_and_mh"""

        return set([x.asn for x in engine.stubs_and_mh])

#######################
# Adopting ASNs funcs #
#######################

    def _get_non_default_as_cls_dict(self, engine, percent_adoption, prev_scenario):
        """Returns as class dict

        non_default_as_cls_dict is a dict of asn: AdoptASCls
        where you do __not__ include any of the BaseASCls,
        since that is the default

        By default, we use the previous engine input to maintain static
        adoption across trials
        """

        # By default, use the last engine input to maintain static
        # adoption across the graph
        if prev_scenario:
            # TODO: get as_cls_dict from previous engine input
            return {asn: self.AdoptASCls for asn, ASCls in
                    prev_engine_input.non_default_as_cls_dict.items()}
        else:
            return {asn: self.AdoptASCls for asn in
                    self._get_adopting_asns(engine, percent_adoption)}

    def _get_adopting_asns(self, engine, percent_adopt):
        """Get adopting ASNs

        By default, to get even adoption, adopt in each of the three
        subcategories"""

        adopting_asns = list()
        subcategories = ("stubs_and_mh", "middle_tier", "input_clique")
        for subcategory in subcategories:
            for ases in getattr(engine, subcategory):
                asns = set([x.asn for x in ases])
                # Remove ASes that are already pre-set
                # Ex: Attacker and victim
                # Ex: ROV Nodes (in certain situations)
                possible_adopters = asns.difference(self._preset_asns)
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
        adopting_asns += self._default_adopters
        assert len(adopting_asns) == len(set(adopting_asns))
        return adopting_asns

    @property
    def _default_adopters(self):
        """By default, victim always adopts"""

        return [self.victim_asn]

    @property
    def _default_non_adopters(self):
        """By default, attacker always does not adopt"""

        return [self.attacker_asn]

    @property
    def _preset_asns(self):
        """ASNs that have a preset adoption policy"""

        return set(self._default_adopters + self._default_non_adopters)

##############
# Yaml Funcs #
##############

    def __to_yaml_dict__(self):
        """This optional method is called when you call yaml.dump()"""

        return {"attacker_asn": self.attacker_asn,
                "victim_asn": self.victim_asn,
                "non_default_as_cls_dict": {asn: AS.subclass_to_name_dict[ASCls]
                                 for asn, ASCls in self.non_default_as_cls_dict.items()}}

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """This optional method is called when you call yaml.load()"""

        as_classes = {asn: AS.name_to_subclass_dict[name]
                      for asn, name in dct["non_default_as_cls_dict"].items()}

        return cls(attacker_asn=dct["attacker_asn"],
                   victim_asn=dct["victim_asn"],
                   non_default_as_cls_dict=as_classes)
