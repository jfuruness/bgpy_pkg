from typing import TYPE_CHECKING

from bgpy.enums import Prefixes
from bgpy.enums import Timestamps

from bgpy.simulation_framework.scenarios.custom_scenarios.victims_prefix import (
    VictimsPrefix
)

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ShortestPathHijack(VictimsPrefix):
    """Shortest path allowed by defense set by AdoptPolicyCls against a prefix"""

    def _get_announcements(self, *args, **kwargs) -> tuple["Ann", ...]:
        """Returns the two announcements seeded for this engine input

        This engine input is for a prefix hijack,
        consisting of a valid prefix and invalid prefix with path manipulation
        """

        # First get the victims prefix
        victim_anns = super()._get_announcements(*args, **kwargs)
        attacker_anns = self._get_shortest_path_attacker_anns(*args, **kwargs)
        return victim_anns + attacker_anns

    def _get_shortest_path_attacker_anns(self, *args, **kwargs) -> tuple["Ann", ...]:
        """Returns announcements for the shortest path attacker"""

        if self.scenario_config.AdoptPolicyCls in self.pre_rov_policy_classes:
            return self._get_prefix_attacker_anns(*args, **kwargs)
        elif self.scenario_config.AdoptPolicyCls in self.rov_policy_classes:
            return self._get_forged_origin_attack_anns(*args, **kwargs)
        elif self.scenario_config.AdoptPolicyCls in (PathEnd, PathEndFull):
            return self._get_pathend_attack_anns(*args, **kwargs)
        elif self.scenario_config.AdoptPolicyCls in (ASPA, ASPAFull):
            return self._get_aspa_attack_anns(*args, **kwargs)
        else:
            raise NotImplementedError(
                "Need to code shortest path attack against "
                f"{self.scenario_config.AdoptPolicyCls}"
            )

    _get_prefix_attacker_anns = PrefixHijack._get_prefix_attacker_anns
    _get_forged_origin_attacker_anns = (
        ForgedOriginHijack._get_forged_origin_attacker_anns
    )

    def _get_pathend_attack_anns(self, *args, **kwargs) -> tuple["Ann"]:
        """Get shortest path undetected by Path-End"""

        raise NotImplementedError

    def _get_aspa_attack_anns(self, *args, **kwargs) -> tuple["Ann"]:
        """Get shortest path undetected by ASPA"""

        raise NotImplementedError

    ######################
    # Policy class lists #
    ######################

    @property
    def pre_rov_policy_classes(self) -> frozenset[type[Policy], ...]:
        """These are policy classes that are susceptible to pre_rov attacks

        such as prefix hijack, subprefix hijack
        """

        return frozenset(
            {BGP, BGPFull, BGPSec, BGPSecFull, OnlyToCustomers, OnlyToCustomersFull}
        )

    @property
    def rov_policy_classes(self) -> frozenset[type[Policy], ...]:
        """These are policy classes that are susceptible to forged-origin attacks"""

        return frozenset(
            {ROV,
             ROVFull,
             PeerROV,
             PeerROVFull,
             ROVPPV1Lite,
             ROVPPV1LiteFull,
             ROVPPV2Lite,
             ROVPPV2LiteFull,
             ROVPPV2ImprovedList,
             ROVPPV2ImprovedLiteFull
            }
        )
