from .base_scenarios import SingleAtkVicAdoptClsScenario
from ..announcements import generate_ann
from ..enums import Prefixes
from ..enums import Timestamps


class ValidPrefix(SingleAtkVicAdoptClsScenario):
    """A valid prefix engine input, mainly for testing"""

    __slots__ = ()

    def _get_announcements(self, **ann_subclass_defaults):
        """Returns a valid prefix announcement

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

        return (generate_ann(**vic_ann_attrs, **ann_subclass_defaults),)
