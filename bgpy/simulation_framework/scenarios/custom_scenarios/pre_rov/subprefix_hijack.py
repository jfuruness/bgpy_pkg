from typing import TYPE_CHECKING

from bgpy.scenarios.custom_scenarios.victims_prefix import VictimsPrefix
from bgpy.enums import Prefixes
from bgpy.enums import Timestamps


if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class SubprefixHijack(VictimsPrefix):
    """Subprefix Hijack Scenario

    Subprefix hijack consists of a valid prefix by the victim with a roa
    then a subprefix from an attacker
    invalid by roa by length and origin
    """

    def _get_announcements(self, *args, **kwargs) -> tuple["Ann", ...]:
        """Returns victim and attacker anns for subprefix hijack

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        # First get victim's anns
        anns = list(super()._get_announcements(*args, **kwargs))

        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.SUBPREFIX.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                )
            )
        return tuple(anns)
