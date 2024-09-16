from typing import TYPE_CHECKING, Optional

from bgpy.shared.enums import Prefixes, Timestamps
from bgpy.simulation_framework.scenarios.custom_scenarios.victims_prefix import (
    VictimsPrefix,
)

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class ForgedOriginPrefixHijack(VictimsPrefix):
    """Extension of prefix hijack where attacker appends legit origin to avoid ROV

    Same ROAs as the VictimsPrefix, which is why we subclassed it it
    """

    def _get_announcements(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Returns the two announcements seeded for this engine input

        This engine input is for a prefix hijack,
        consisting of a valid prefix and invalid prefix with path manipulation
        """

        # First get the victims prefix
        victim_anns = super()._get_announcements(engine=engine)
        attacker_anns = self._get_forged_origin_attacker_anns(engine=engine)
        return victim_anns + attacker_anns

    def _get_forged_origin_attacker_anns(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Returns attacker anns for a forged origin hijack"""

        victim_asn = next(iter(self.victim_asns))

        anns = list()
        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(attacker_asn, victim_asn),
                    timestamp=Timestamps.ATTACKER.value,
                    next_hop_asn=attacker_asn,
                    seed_asn=attacker_asn,
                )
            )
        return tuple(anns)
