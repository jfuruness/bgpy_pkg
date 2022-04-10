from .engine_input import EngineInput
from ..announcements import generate_ann
from ..enums import Prefixes
from ..enums import Timestamps


class PrefixHijack(EngineInput):
    """Prefix hijack where both attacker and victim compete for a prefix"""

    __slots__ = ()

    def _get_announcements(self, **ann_subclass_defaults):
        """Returns the two announcements seeded for this engine input

        This engine input is for a prefix hijack,
        consisting of a valid prefix and invalid prefix

        generate_ann generates announcements with Announcement class defaults
        (for example, withdraw=False to indicate the announcement is not
        a withdrawal)
        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement, and pass in any additional
        defaults via ann_subclass_defaults
        """

        # Victim ann attrs
        vic_ann_attrs = {"AnnCls": self.AnnCls,
                         "origin_asn": self.victim_asn,
                         "prefix": Prefixes.PREFIX.value,
                         "timestamp": Timestamps.VICTIM.value,
                         "roa_valid_length": True,
                         "roa_origin": self.victim_asn}

        # Attacker ann attrs
        atk_ann_attrs = {"AnnCls": self.AnnCls,
                         "origin_asn": self.attacker_asn,
                         "prefix": Prefixes.PREFIX.value,
                         "timestamp": Timestamps.ATTACKER.value,
                         "roa_valid_length": True,
                         "roa_origin": self.victim_asn}

        return (generate_ann(**vic_ann_attrs, **ann_subclass_defaults),
                generate_ann(**atk_ann_attrs, **ann_subclass_defaults))
