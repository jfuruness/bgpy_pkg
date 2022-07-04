from ..base_scenarios import SingleAtkVicAdoptClsScenario
from ...enums import Prefixes
from ...enums import Relationships
from ...enums import Timestamps


class PrefixHijack(SingleAtkVicAdoptClsScenario):
    """Prefix hijack where both attacker and victim compete for a prefix"""

    __slots__ = ()

    def _get_announcements(self):
        """Returns the two announcements seeded for this engine input

        This engine input is for a prefix hijack,
        consisting of a valid prefix and invalid prefix

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        vic_ann = self.AnnCls(prefix=Prefixes.PREFIX.value,
                              as_path=(self.victim_asn,),
                              timestamp=Timestamps.VICTIM.value,
                              seed_asn=self.victim_asn,
                              roa_valid_length=True,
                              roa_origin=self.victim_asn,
                              recv_relationship=Relationships.ORIGIN)

        atk_ann = self.AnnCls(prefix=Prefixes.PREFIX.value,
                              as_path=(self.attacker_asn,),
                              timestamp=Timestamps.ATTACKER.value,
                              seed_asn=self.attacker_asn,
                              roa_valid_length=True,
                              roa_origin=self.victim_asn,
                              recv_relationship=Relationships.ORIGIN)

        return vic_ann, atk_ann
