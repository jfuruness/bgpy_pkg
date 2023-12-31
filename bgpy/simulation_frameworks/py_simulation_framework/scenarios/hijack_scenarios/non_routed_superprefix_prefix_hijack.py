from typing import TYPE_CHECKING, Union

from bgpy.simulation_frameworks.py_simulation_framework.scenarios.scenario import (
    Scenario,
)
from bgpy.enums import Prefixes
from bgpy.enums import CPPRelationships
from bgpy.enums import Timestamps


if TYPE_CHECKING:
    from bgpy.simulation_engines.cpp_simulation_engine import CPPAnnouncement as CPPAnn
    from bgpy.simulation_engines.py_simulation_engine import PyAnnouncement as PyAnn


class NonRoutedSuperprefixPrefixHijack(Scenario):
    """Non routed superprefix prefix hijack

    Attacker has a superprefix with an unknown ROA,
    along with a prefix with a known ROA
    hijacking a non routed prefix that has a non routed ROA
    """

    def _get_announcements(
        self, *args, **kwargs
    ) -> tuple[Union["CPPAnn", "PyAnn"], ...]:
        """Returns a superprefix announcement for this engine input

        for subclasses of this EngineInput, you can set AnnCls equal to
        something other than Announcement
        """

        anns = list()
        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix_block_id=1,
                    prefix=Prefixes.SUPERPREFIX.value,
                    as_path=[attacker_asn,],
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    roa_valid_length=None,
                    roa_origin=None,
                    recv_relationship=CPPRelationships.ORIGIN,
                )
            )
            anns.append(
                self.scenario_config.AnnCls(
                    prefix_block_id=0,
                    prefix=Prefixes.PREFIX.value,
                    as_path=[attacker_asn,],
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    roa_valid_length=True,
                    roa_origin=0,
                    recv_relationship=CPPRelationships.ORIGIN,
                )
            )

        return tuple(anns)
