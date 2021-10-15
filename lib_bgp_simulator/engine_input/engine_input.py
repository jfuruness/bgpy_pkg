import random

from ipaddress import ip_network

from ..announcements import Announcement
from ..enums import Outcomes, Relationships


class EngineInput:
    """Contains information regarding an attack"""

    __slots__ = ("attacker_asn", "victim_asn", "adopting_asns",
                 "announcements")

    AnnCls = Announcement

    y_labels = {Outcomes.ATTACKER_SUCCESS: "Percent Attacker Success",
                Outcomes.VICTIM_SUCCESS: "Percent Legitimate Origin Success",
                Outcomes.DISCONNECTED: "Percent Disconnected"}

    def __init__(self, subgraph_asns, engine, percent_adopt):
        self.attacker_asn = self._get_attacker_asn(subgraph_asns, engine)
        self.victim_asn = self._get_victim_asn(subgraph_asns, engine)
        self.adopting_asns = self._get_adopting_asns(subgraph_asns, engine, percent_adopt)
        self.announcements = self._get_announcements()
        # Announcement prefixes must overlap
        # If they don't, traceback wouldn't work
        first_prefix = ip_network(self.announcements[0].prefix)
        for ann in self.announcements:
            assert ip_network(ann.prefix).overlaps(first_prefix)


    def seed(self, engine):
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
        """This assumes that the as_obj is the last in the path"""

        if self.attacker_asn == as_obj.asn:
            return Outcomes.ATTACKER_SUCCESS
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

        # Keep going
        else:
            return None

    def post_propagation_hook(self, *args, **kwargs):
        pass

##############################
# Select Attacker and victim #
##############################

    def _get_attacker_asn(self, subgraphs, engine):
        possible_attacker_asns = self._possible_attackers(subgraphs, engine)
        return random.choice(tuple(possible_attacker_asns))

    def _possible_attackers(self, subgraph_asns, engine):
        return subgraph_asns["stubs_and_mh"]

    def _get_victim_asn(self, subgraph_asns, engine):
        possible_vic_asns = self._possible_victims(subgraph_asns, engine)
        return random.choice(tuple(possible_vic_asns.difference([self.attacker_asn])))

    def _possible_victims(self, subgraph_asns, engine):
        return subgraph_asns["stubs_and_mh"]

#######################
# Adopting ASNs funcs #
#######################

    def _get_adopting_asns(self, subgraph_asns, engine, percent_adopt):
        adopting_asns = list()
        for asns in subgraph_asns.values():
            possible_adopters = asns.difference(self.uncountable_asns)
            # Get how many ASes should be adopting
            k = len(possible_adopters) * percent_adopt // 100
            # Round for the start and end of the graph
            if k == 0:
                k += 1
            elif k == len(possible_adopters):
                k -= 1

            adopting_asns.extend(random.sample(possible_adopters, k))
        adopting_asns += self._default_adopters()
        assert len(adopting_asns) == len(set(adopting_asns))
        return adopting_asns

    def _default_adopters(self):
        return [self.victim_asn]

    def _default_non_adopters(self):
        return [self.attacker_asn]

    @property
    def uncountable_asns(self):
        """ASNs that we do not count for statistics since they are defaults"""

        return self._default_adopters() + self._default_non_adopters()

    def get_as_classes(self, engine, BaseASCls, AdoptingASCls):
        return {asn: AdoptingASCls for asn in self.adopting_asns}

################
# Helper Funcs #
################

    def _get_prefix_subprefix_dict(self):
        prefixes = set([])
        for ann in self.recv_q.announcements:
            prefixes.add(ann.prefix)
        # Do this here for speed
        prefixes = [ip_network(x) for x in prefixes]

        for prefix in prefixes:
            # Supported in python3.7, not by pypy yet
            def subnet_of(other):
                return str(prefix) in [str(x) for x in other.subnets()]
            prefix.subnet_of = subnet_of

        prefix_subprefix_dict = {x: [] for x in prefixes}
        for outer_prefix, subprefix_list in prefix_subprefix_dict.items():
            for prefix in prefixes:
                if prefix.subnet_of(outer_prefix):
                    subprefix_list.append(str(prefix))
        # Get rid of ip_network
        return {str(k): v for k, v in prefix_subprefix_dict.items()}
