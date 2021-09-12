from ipaddress import ip_network

class Attack:
    """Contains information regarding an attack"""

    __slots__ = ["attacker_asn", "victim_asn", "announcements", "post_run_hooks"]

    def __init__(self, attacker: int, victim: int, announcements: list, post_run_hooks=None):
        self.attacker_asn = attacker
        self.victim_asn = victim
        self.announcements = announcements
        # post_run_hooks is a list of functions to be called after the scenario
        # is run and before the engine is deleted.
        self.post_run_hooks = [] if post_run_hooks is None else post_run_hooks

        # Announcement prefixes must overlap
        # If they don't, traceback wouldn't work
        first_prefix = ip_network(self.announcements[0].prefix)
        for ann in self.announcements:
            assert ip_network(ann.prefix).overlaps(first_prefix)
