from ..base_scenarios import SingleAtkVicAdoptClsScenario
from ...enums import Prefixes
from ...enums import Relationships
from ...enums import Timestamps


class SuperprefixPrefixHijack(SingleAtkVicAdoptClsScenario):
    """Superprefix prefix attack

    This is an attack where the attacker
    announces a prefix hijack (invalid by roa origin)
    and also announces a superprefix of the prefix (ROA unknown)
    and the victim announces their own prefix
    """

    __slots__ = ()

    def _get_announcements(self):
        """Returns victim+attacker prefix ann, attacker superprefix ann

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
        atk_superprefix = self.AnnCls(prefix=Prefixes.SUPERPREFIX.value,
                                      as_path=(self.attacker_asn,),
                                      timestamp=Timestamps.ATTACKER.value,
                                      seed_asn=self.attacker_asn,
                                      roa_valid_length=None,
                                      roa_origin=None,
                                      recv_relationship=Relationships.ORIGIN)
        return vic_ann, atk_ann, atk_superprefix
