from .engine_input import EngineInput
from ..announcements import generate_ann
from ..enums import Prefixes
from ..enums import Timestamps


class NonRoutedPrefixHijack(EngineInput):
    """Non routed prefix hijack (ROA of AS 0)"""

    __slots__ = ()

    def _get_announcements(self, **ann_subclass_defaults):
        """Returns non routed prefix announcement from attacker

        generate_ann generates announcements with Announcement class defaults
        (for example, withdraw=False to indicate the announcement is not 
        a withdrawal)
        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement, and pass in any additional
        defaults via ann_subclass_defaults
        """

        atk_ann_attrs = {"AnnCls": self.AnnCls,
                         "origin_asn": self.attacker_asn,
                         "prefix": Prefixes.PREFIX.value,
                         "timestamp": Timestamps.ATTACKER.value,
                         "roa_valid_length": True,
                         "roa_origin": 0}

        return (generate_ann(**atk_ann_attrs, **ann_subclass_defaults),)
