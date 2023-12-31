from typing import TYPE_CHECKING, Union

from .scenario import Scenario
from bgpy.enums import Prefixes
from bgpy.enums import CPPRelationships
from bgpy.enums import Timestamps


if TYPE_CHECKING:
    from bgpy.simulation_engines.cpp_simulation_engine import CPPAnnouncement as CPPAnn
    from bgpy.simulation_engines.py_simulation_engine import PyAnnouncement as PyAnn


class ValidPrefix(Scenario):
    """A valid prefix engine input, mainly for testing"""

    def _get_announcements(
        self, *args, **kwargs
    ) -> tuple[Union["CPPAnn", "PyAnn"], ...]:
        """Returns a valid prefix announcement

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix_block_id=0,
                    prefix=Prefixes.PREFIX.value,
                    as_path=[victim_asn,],
                    timestamp=Timestamps.VICTIM.value,
                    seed_asn=victim_asn,
                    roa_valid_length=True,
                    roa_origin=victim_asn,
                    recv_relationship=CPPRelationships.ORIGIN,
                )
            )
        return tuple(anns)

    def _get_attacker_asns(self, *args, **kwargs):
        return set()
