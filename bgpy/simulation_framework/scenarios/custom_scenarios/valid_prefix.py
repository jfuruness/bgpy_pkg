from .victims_prefix import VictimsPrefix


class ValidPrefix(VictimsPrefix):
    """Victims prefixes only - with no attackers!"""

    def _get_attacker_asns(self, *args, **kwargs):
        return set()
