class Attack:
    """Contains information regarding an attack"""

    def __init__(self, attacker: int, victim: int, announcements: list):
        self.attacker_asn = attacker
        self.victim_asn = victim
        self.announcements = announcements

        # Announcement prefixes must overlap
        # If they don't, traceback wouldn't work
        first_prefix = ip_network(self.announcements[0].prefix)
        for ann in self.announcements:
            assert ip_network(ann.prefix).overlaps(first_prefix)
