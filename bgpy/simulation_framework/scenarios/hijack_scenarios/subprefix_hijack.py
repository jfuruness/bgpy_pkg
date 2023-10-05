from typing import TYPE_CHECKING

from bgpy.simulation_framework.scenarios.scenario import Scenario
from bgpy.enums import Prefixes
from bgpy.enums import Relationships
from bgpy.enums import Timestamps


if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement


class SubprefixHijack(Scenario):
    """Subprefix Hijack Engine input

    Subprefix hijack consists of a valid prefix by the victim with a roa
    then a subprefix from an attacker
    invalid by roa by length and origin
    """

    def _get_announcements(self, *args, **kwargs) -> tuple["Announcement", ...]:
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
                    seed_asn=victim_asn,
                    roa_valid_length=True,
                    roa_origin=victim_asn,
                    recv_relationship=Relationships.ORIGIN,
                )
            )

        err: str = "Fix the roa_origins of the " "announcements for multiple victims"
        assert len(self.victim_asns) == 1, err

        roa_origin: int = next(iter(self.victim_asns))

        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.SUBPREFIX.value,
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    roa_valid_length=False,
                    roa_origin=roa_origin,
                    recv_relationship=Relationships.ORIGIN,
                )
            )
        return tuple(anns)
