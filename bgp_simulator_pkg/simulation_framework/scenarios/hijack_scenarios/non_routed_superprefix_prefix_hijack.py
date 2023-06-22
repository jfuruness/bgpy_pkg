from typing import TYPE_CHECKING

from ..scenario import Scenario
from ....enums import Prefixes
from ....enums import Relationships
from ....enums import Timestamps


if TYPE_CHECKING:
    from ....simulation_engine import Announcement


class NonRoutedSuperprefixPrefixHijack(Scenario):
    """Non routed superprefix prefix hijack

    Attacker has a superprefix with an unknown ROA,
    along with a prefix with a known ROA
    hijacking a non routed prefix that has a non routed ROA
    """

    __slots__ = ()  # type: ignore

    def _get_announcements(self, *args, **kwargs) -> tuple["Announcement", ...]:
        """Returns a superprefix announcement for this engine input

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        anns = list()
        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.SUPERPREFIX.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    roa_valid_length=None,
                    roa_origin=None,
                    recv_relationship=Relationships.ORIGIN,
                )
            )
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    roa_valid_length=True,
                    roa_origin=0,
                    recv_relationship=Relationships.ORIGIN,
                )
            )

        return tuple(anns)
