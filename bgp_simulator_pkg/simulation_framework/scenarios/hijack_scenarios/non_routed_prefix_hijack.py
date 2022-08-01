from __future__ import annotations
from typing import Tuple, TYPE_CHECKING

from ..scenario import Scenario
from ....enums import Prefixes
from ....enums import Relationships
from ....enums import Timestamps


if TYPE_CHECKING:
    from ....simulation_engine import Announcement


class NonRoutedPrefixHijack(Scenario):
    """Non routed prefix hijack (ROA of AS 0)"""

    __slots__ = ()

    def _get_announcements(self) -> Tuple["Announcement", ...]:
        """Returns non routed prefix announcement from attacker

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        anns = list()
        for attacker_asn in self.attacker_asns:
            anns.append(self.AnnCls(prefix=Prefixes.PREFIX.value,
                                    as_path=(attacker_asn,),
                                    timestamp=Timestamps.ATTACKER.value,
                                    seed_asn=attacker_asn,
                                    roa_valid_length=True,
                                    roa_origin=0,
                                    recv_relationship=Relationships.ORIGIN))
        return tuple(anns)
