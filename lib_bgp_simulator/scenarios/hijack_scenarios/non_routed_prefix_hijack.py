from ..base_scenarios import SingleAtkVicAdoptClsScenario
from ...enums import Prefixes
from ...enums import Relationships
from ...enums import Timestamps


class NonRoutedPrefixHijack(SingleAtkVicAdoptClsScenario):
    """Non routed prefix hijack (ROA of AS 0)"""

    __slots__ = ()

    def _get_announcements(self):
        """Returns non routed prefix announcement from attacker

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        ann = self.AnnCls(prefix=Prefixes.PREFIX.value,
                          as_path=(self.attacker_asn,),
                          timestamp=Timestamps.ATTACKER.value,
                          seed_asn=self.attacker_asn,
                          roa_valid_length=True,
                          roa_origin=0,
                          recv_relationship=Relationships.ORIGIN)
        return (ann,)
