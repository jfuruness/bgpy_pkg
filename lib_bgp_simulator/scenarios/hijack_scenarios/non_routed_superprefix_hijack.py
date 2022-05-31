from ..base_scenarios import SingleAtkVicAdoptClsScenario
from ...announcements import generate_ann
from ...enums import Prefixes
from ...enums import Timestamps


class NonRoutedSuperprefixHijack(SingleAtkVicAdoptClsScenario):
    """Non routed superprefix hijack

    Attacker has a superprefix with an unknown ROA,
    hijacking a non routed prefix that has a non routed ROA
    """

    __slots__ = ()

    def _get_announcements(self, **ann_subclass_defaults):
        """Returns a superprefix announcement for this engine input

        generate_ann generates announcements with Announcement class defaults
        (for example, withdraw=False to indicate the announcemnt is not
        a withdrawal)
        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement, and pass in any additional
        defaults via ann_subclass_defaults
        """

        atk_ann_attrs = {"AnnCls": self.AnnCls,
                         "origin_asn": self.attacker_asn,
                         "seed_asn": self.attacker_asn,
                         "prefix": Prefixes.SUPERPREFIX.value,
                         "timestamp": Timestamps.ATTACKER.value,
                         "roa_valid_length": None,
                         "roa_origin": None}

        return (generate_ann(**atk_ann_attrs, **ann_subclass_defaults),)
