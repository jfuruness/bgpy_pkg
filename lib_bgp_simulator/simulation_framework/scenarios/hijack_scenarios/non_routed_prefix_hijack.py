from ..scenario import Scenario
from ....enums import Prefixes
from ....enums import Relationships
from ....enums import Timestamps
from ....simulation_engine import Announcement as Ann

class NonRoutedPrefixHijack(Scenario):
    """Non routed prefix hijack (ROA of AS 0)"""

    __slots__ = ()  # type: ignore

    def _get_announcements(self) -> tuple:
        """Returns non routed prefix announcement from attacker

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        anns: list = list()
        for attacker_asn in self.attacker_asns:
            anns.append(self.AnnCls(prefix=Prefixes.PREFIX.value,
                                    as_path=(attacker_asn,),
                                    timestamp=Timestamps.ATTACKER.value,
                                    seed_asn=attacker_asn,
                                    roa_valid_length=True,
                                    roa_origin=0,
                                    recv_relationship=Relationships.ORIGIN))
        return tuple(anns)
