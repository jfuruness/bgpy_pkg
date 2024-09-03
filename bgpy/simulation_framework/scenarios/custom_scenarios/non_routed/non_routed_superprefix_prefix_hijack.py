from ipaddress import ip_network
from typing import TYPE_CHECKING, Optional

from roa_checker import ROA

from bgpy.shared.enums import Prefixes, Timestamps
from bgpy.simulation_framework.scenarios.scenario import Scenario

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class NonRoutedSuperprefixPrefixHijack(Scenario):
    """Non routed superprefix prefix hijack

    Attacker has a superprefix with an unknown ROA,
    along with a prefix with a known ROA
    hijacking a non routed prefix that has a non routed ROA
    """

    def _get_announcements(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
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

    def _get_roas(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple[ROA, ...]:
        """Returns a tuple of ROAs

        Not abstract and by default does nothing for
        backwards compatability
        """

        return (ROA(ip_network(Prefixes.PREFIX.value), 0),)
