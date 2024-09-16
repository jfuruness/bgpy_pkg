from typing import TYPE_CHECKING, Optional

from bgpy.shared.enums import Prefixes, Timestamps
from bgpy.simulation_framework.scenarios.custom_scenarios.victims_prefix import (
    VictimsPrefix,
)

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class SubprefixHijack(VictimsPrefix):
    """Subprefix Hijack Scenario

    Subprefix hijack consists of a valid prefix by the victim with a roa
    then a subprefix from an attacker
    invalid by roa by length and origin
    """

    def _get_announcements(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Returns victim and attacker anns for subprefix hijack

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        # First get victim's anns
        victim_anns = super()._get_announcements(engine=engine)
        assert isinstance(victim_anns, tuple), "mypy"
        attacker_anns = self._get_subprefix_attacker_anns(engine=engine)
        return victim_anns + attacker_anns

    def _get_subprefix_attacker_anns(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Returns subprefix announcements from the attacker"""

        anns = list()
        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.SUBPREFIX.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                )
            )
        return tuple(anns)
