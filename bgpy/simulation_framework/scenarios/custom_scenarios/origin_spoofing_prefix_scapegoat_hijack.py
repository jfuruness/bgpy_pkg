from typing import Optional, Union, TYPE_CHECKING

from bgpy.simulation_framework.scenarios.scenario import Scenario
from bgpy.enums import Prefixes
from bgpy.enums import Relationships
from bgpy.enums import SpecialPercentAdoptions
from bgpy.enums import Timestamps

from .origin_spoofing_prefix_disconnection_hijack import (
    OriginSpoofingPrefixDisconnectionHijack,
)


if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine
    from bgpy.simulation_engine import Policy


class OriginSpoofingPrefixScapegoatHijack(OriginSpoofingPrefixDisconnectionHijack):
    """Prefix hijack where both attacker and victim compete for a prefix

    Attacker spoofs origin to be victim to bypass roas, and sets the next hop
    of the providers"""

    def _get_announcements(
        self, engine: "BaseSimulationEngine", *args, **kwargs
    ) -> tuple["Ann", ...]:
        """Returns the two announcements seeded for this engine input"""

        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    next_hop_asn=victim_asn,
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

        # Oof
        self._scapegoat_asns = set()

        for attacker_asn in self.attacker_asns:
            scapegoat = engine.as_graph.as_dict[attacker_asn].customers[0]
            self._scapegoat_asns.add(scapegoat.asn)
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    next_hop_asn=scapegoat.asn,
                    as_path=(victim_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    roa_valid_length=True,
                    roa_origin=roa_origin,
                    recv_relationship=Relationships.ORIGIN,
                )
            )

        return tuple(anns)

    def _get_possible_attacker_asns(
        self,
        engine: "BaseSimulationEngine",
        percent_adoption: Union[float, SpecialPercentAdoptions],
        prev_scenario: Optional["Scenario"],
    ) -> frozenset[int]:
        """Get possible attacker ASNs that have customers

        For now this attack can only scapegoat customers
        """

        possible_attacker_asns = super()._get_possible_attacker_asns(
            engine, percent_adoption, prev_scenario
        )
        remove_attacker_asns = set()
        for asn in possible_attacker_asns:
            # For now this attack only does customer scapegoating
            if not engine.as_graph.as_dict[asn].customers:
                remove_attacker_asns.add(asn)
        rv = possible_attacker_asns.difference(remove_attacker_asns)
        assert rv, (
            "No possible attackers? Are you not choosing from transit ASes?\n"
            "For now this policy can only scapegoat customers, so attacker needs "
            "customers"
        )
        return rv

    def _generate_policy_cls(self, PolicyCls: type["Policy"]) -> type["Policy"]:
        """Generates the Spoofing scapegoating Attacker policy class

        This is a dynamic subclass of the attacker's class
        """

        # mypy can't handle dynamic base classes
        # https://github.com/python/mypy/issues/2477
        class SpoofingScapegoatingAttacker(PolicyCls):  # type: ignore
            name = "Spoofing scapegoating attacker"

            def _policy_propagate(
                s,
                neighbor: "AS",
                ann: "Ann",
                propagate_to: Relationships,
                send_rels: set[Relationships],
            ) -> bool:
                # Don't send the hijack to the scapegoat
                return neighbor.asn in self._scapegoat_asns

        return SpoofingScapegoatingAttacker
