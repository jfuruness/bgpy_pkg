from ..base_scenarios import SingleAtkVicAdoptClsScenario
from ...enums import Prefixes
from ...enums import Relationships
from ...enums import Timestamps


class NonRoutedSuperprefixHijack(SingleAtkVicAdoptClsScenario):
    """Non routed superprefix hijack

    Attacker has a superprefix with an unknown ROA,
    hijacking a non routed prefix that has a non routed ROA
    """

    __slots__ = ()

    def _get_announcements(self):
        """Returns a superprefix announcement for this engine input

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        ann = self.AnnCls(prefix=Prefixes.SUPERPREFIX.value,
                          as_path=(self.attacker_asn,),
                          timestamp=Timestamps.ATTACKER.value,
                          seed_asn=self.attacker_asn,
                          roa_valid_length=None,
                          roa_origin=None,
                          recv_relationship=Relationships.ORIGIN)

        return (ann,)
