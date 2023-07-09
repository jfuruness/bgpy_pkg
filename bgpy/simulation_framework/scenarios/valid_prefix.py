from typing import TYPE_CHECKING

from .scenario import Scenario
from bgpy.enums import Prefixes
from bgpy.enums import Relationships
from bgpy.enums import Timestamps


if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement


class ValidPrefix(Scenario):
    """A valid prefix engine input, mainly for testing"""

    def _get_announcements(self, *args, **kwargs) -> tuple["Announcement", ...]:
        """Returns a valid prefix announcement

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(victim_asn,),
                    timestamp=Timestamps.VICTIM.value,
                    seed_asn=victim_asn,
                    roa_valid_length=True,
                    roa_origin=victim_asn,
                    recv_relationship=Relationships.ORIGIN,
                )
            )
        return tuple(anns)

    def _get_attacker_asns(self, *args, **kwargs):
        return set()
