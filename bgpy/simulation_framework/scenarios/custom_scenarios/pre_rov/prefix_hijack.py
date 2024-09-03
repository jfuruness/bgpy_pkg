from typing import TYPE_CHECKING, Optional

from bgpy.shared.enums import Prefixes, Timestamps
from bgpy.simulation_framework.scenarios.custom_scenarios.victims_prefix import (
    VictimsPrefix,
)

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class PrefixHijack(VictimsPrefix):
    """Prefix hijack where both attacker and victim compete for a prefix"""

    def _get_announcements(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Returns the two announcements seeded for this scenario

        This scenario is for a prefix hijack,
        consisting of a valid prefix and invalid prefix
        """

        # First get the victim's announcements
        victim_anns = super()._get_announcements(engine=engine)
        assert isinstance(victim_anns, tuple), "mypy"
        attacker_anns = self._get_prefix_attacker_anns(engine=engine)
        return victim_anns + attacker_anns

    def _get_prefix_attacker_anns(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Returns attacker's announcements for a prefix hijack"""

        anns = list()
        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                )
            )
        return tuple(anns)
