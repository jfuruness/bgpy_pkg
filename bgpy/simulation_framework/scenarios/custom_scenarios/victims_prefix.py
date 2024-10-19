from ipaddress import ip_network
from typing import TYPE_CHECKING, Optional

from roa_checker import ROA

from bgpy.shared.enums import Prefixes, Relationships, Timestamps
from bgpy.simulation_framework.scenarios.scenario import Scenario

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class VictimsPrefix(Scenario):
    """A Scenario with only the victims prefix

    This is meant to be used as a parent class, so it still has
    attackers, even though only the victims prefix is used
    """

    def _get_announcements(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Returns a valid prefix announcement

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    next_hop_asn=victim_asn,
                    as_path=(victim_asn,),
                    timestamp=Timestamps.VICTIM.value,
                    seed_asn=victim_asn,
                    recv_relationship=Relationships.ORIGIN,
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
