from typing import TYPE_CHECKING

from bgpy.simulation_frameworks.py_simulation_framework.scenarios.scenario import Scenario
from bgpy.enums import Prefixes
from bgpy.enums import CPPRelationships
from bgpy.enums import Timestamps


if TYPE_CHECKING:
    from bgpy.simulation_engines.cpp_simulation_engine import CPPAnnouncement as CPPAnn
    from bgpy.simulation_engines.py_simulation_engine import PyAnnouncement as PyAnn




class NonRoutedPrefixHijack(Scenario):
    """Non routed prefix hijack (ROA of AS 0)"""

    def _get_announcements(self, *args, **kwargs) -> tuple["CPPAnn" | "PyAnn", ...]:
        """Returns non routed prefix announcement from attacker

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        anns = list()
        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    roa_valid_length=True,
                    roa_origin=0,
                    recv_relationship=CPPRelationships.ORIGIN,
                )
            )
        return tuple(anns)
