from typing import TYPE_CHECKING, Optional

from bgpy.shared.enums import Prefixes, Timestamps
from bgpy.simulation_framework.scenarios.custom_scenarios.victims_prefix import (
    VictimsPrefix,
)

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine


class SuperprefixPrefixHijack(VictimsPrefix):
    """Superprefix prefix attack

    This is an attack where the attacker
    announces a prefix hijack (invalid by roa origin)
    and also announces a superprefix of the prefix (ROA unknown)
    and the victim announces their own prefix
    """

    def _get_announcements(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Returns victim+attacker prefix ann, attacker superprefix ann"""

        # First get anns for the victim
        anns = list(super()._get_announcements(engine=engine))

        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                )
            )
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.SUPERPREFIX.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                )
            )

        return tuple(anns)
