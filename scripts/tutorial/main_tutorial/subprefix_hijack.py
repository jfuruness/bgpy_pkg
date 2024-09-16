from ipaddress import ip_network
from typing import TYPE_CHECKING, Optional

from roa_checker import ROA

from bgpy.shared.enums import Prefixes, Timestamps
from bgpy.simulation_framework.scenarios.scenario import Scenario

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class SubprefixHijack(Scenario):
    """Subprefix Hijack Engine input

    Subprefix hijack consists of a valid prefix by the victim with a roa
    then a subprefix from an attacker
    invalid by roa by length and origin
    """

    def _get_announcements(self, *args, **kwargs) -> tuple["Ann", ...]:
        """Returns victim and attacker anns for subprefix hijack

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
                )
            )

        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.SUBPREFIX.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                )
            )
        return tuple(anns)

    def _get_roas(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple[ROA, ...]:
        """Returns a tuple of ROAs"""

        return tuple(
            [ROA(ip_network(Prefixes.PREFIX.value), x) for x in self.victim_asns]
        )
