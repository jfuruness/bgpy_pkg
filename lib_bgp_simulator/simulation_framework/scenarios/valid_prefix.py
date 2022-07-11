from .scenario import Scenario
from ..enums import Prefixes
from ..enums import Relationships
from ..enums import Timestamps


class ValidPrefix(Scenario):
    """A valid prefix engine input, mainly for testing"""

    __slots__ = ()

    def _get_announcements(self):
        """Returns a valid prefix announcement

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(self.AnnCls(prefix=Prefixes.PREFIX.value,
                                    as_path=(victim_asn,),
                                    timestamp=Timestamps.VICTIM.value,
                                    seed_asn=victim_asn,
                                    roa_valid_length=True,
                                    roa_origin=victim_asn,
                                    recv_relationship=Relationships.ORIGIN))
        return tuple(anns)

    def _get_attacker_asns(self, *args, **kwargs):
        return None
