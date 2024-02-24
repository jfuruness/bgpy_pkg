from typing import Optional, TYPE_CHECKING

from bgpy.simulation_framework.scenarios.scenario import Scenario
from bgpy.simulation_framework.scenarios.roa_info import ROAInfo
from bgpy.enums import Prefixes
from bgpy.enums import Timestamps


if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class NonRoutedSuperprefixPrefixHijack(Scenario):
    """Non routed superprefix prefix hijack

    Attacker has a superprefix with an unknown ROA,
    along with a prefix with a known ROA
    hijacking a non routed prefix that has a non routed ROA
    """

    def _get_announcements(self, *args, **kwargs) -> tuple["Ann", ...]:
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
                )
            )
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                )
            )

        return tuple(anns)

    def _get_roa_infos(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional["BaseSimulationEngine"] = None,
        prev_scenario: Optional["Scenario"] = None,
    ) -> tuple[ROAInfo, ...]:
        """Returns a tuple of ROAInfo's

        Not abstract and by default does nothing for
        backwards compatability
        """

        return (ROAInfo(Prefixes.PREFIX.value, 0),)
