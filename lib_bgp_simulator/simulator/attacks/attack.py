from ipaddress import ip_network

from ...announcement import Announcement
from ...enums import Outcomes, Relationships


class Attack:
    """Contains information regarding an attack"""

    __slots__ = ("attacker_asn", "victim_asn", "announcements", "post_run_hooks", "uncountable_asns", "prefix_subprefix_dict")

    AnnCls = Announcement

    y_labels = {x: f"Percent {x.name.lower()}" for x in list(Outcomes)}

    def __init__(self, attacker: int, victim: int, announcements: list, post_run_hooks=None):
        self.attacker_asn = attacker
        self.victim_asn = victim
        self.uncountable_asns = set([attacker, victim])
        self.announcements = announcements
        # post_run_hooks is a list of functions to be called after the scenario
        # is run and before the engine is deleted.
        self.post_run_hooks = [] if post_run_hooks is None else post_run_hooks

        # Announcement prefixes must overlap
        # If they don't, traceback wouldn't work
        first_prefix = ip_network(self.announcements[0].prefix)
        for ann in self.announcements:
            assert ip_network(ann.prefix).overlaps(first_prefix)

        # Get all the prefix along with their subprefixes
        # self.prefix_subprefix_dict = self._get_prefix_subprefix_dict()

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

    def seed(self, as_dict, propagation_round):
        """Seeds announcement at the proper AS

        Since this is the simulator engine, we should
        never have to worry about overlapping announcements
        """

        if propagation_round == 0:
            for ann in self.announcements:
                assert as_dict[ann.seed_asn]._local_rib.get_ann(ann.prefix) is None, "Seeding conflict"

                as_dict[ann.seed_asn]._local_rib.add_ann(ann)


    def _get_prefix_subprefix_dict(self):
        prefixes = set([])
        for ann in policy_self.recv_q.announcements:
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
