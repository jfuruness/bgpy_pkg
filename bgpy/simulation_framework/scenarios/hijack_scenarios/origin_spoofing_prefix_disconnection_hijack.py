from typing import Optional, TYPE_CHECKING

from frozendict import frozendict

from bgpy.simulation_framework.scenarios.scenario import Scenario
from bgpy.enums import Prefixes
from bgpy.enums import Relationships
from bgpy.enums import Timestamps


if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_engine import BaseSimulationEngine
    from bgpy.simulation_engine import Policy


class OriginSpoofingPrefixDisconnectionHijack(Scenario):
    """Prefix hijack where both attacker and victim compete for a prefix

    Attacker spoofs origin to be victim to bypass roas, and sets the next hop
    of the providers"""

    def _get_announcements(self, *args, **kwargs) -> tuple["Ann", ...]:
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

        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    next_hop_asn=attacker_asn,
                    as_path=(victim_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    roa_valid_length=True,
                    roa_origin=roa_origin,
                    recv_relationship=Relationships.ORIGIN,
                )
            )

        return tuple(anns)

    def setup_engine(
        self, engine: "BaseSimulationEngine", prev_scenario: Optional["Scenario"] = None
    ) -> None:
        """Change attacker behavior. Very janky, but for most sims I think this is fine

        esp since this attack won't be frequently used and should be patched quickly
        """

        self.__og_attacker_policies: dict[int, type["Policy"]] = dict()
        for attacker_asn in self.attacker_asns:
            # Get what the attacker class would have been set to
            self.__og_attacker_policies[
                attacker_asn
            ] = self.non_default_asn_cls_dict.get(
                attacker_asn, self.scenario_config.BasePolicyCls
            )

            PolicyCls = self.__og_attacker_policies[attacker_asn]

            non_default = dict(self.non_default_asn_cls_dict)

            non_default[attacker_asn] = self._generate_policy_cls(PolicyCls)

            self.non_default_asn_cls_dict = frozendict(non_default)

        super().setup_engine(engine, prev_scenario)

    def pre_aggregation_hook(
        self, engine: "BaseSimulationEngine", *args, **kwargs
    ) -> None:
        """Puts the OG attacker class back for data analysis"""

        non_default = dict(self.non_default_asn_cls_dict)

        for attacker_asn, OgPolicyCls in self.__og_attacker_policies.items():
            OldPolicyCls = engine.as_graph.as_dict[attacker_asn].policy.__class__
            self.policy_classes_used = frozenset(
                [x for x in self.policy_classes_used if x != OldPolicyCls]
            )

            engine.as_graph.as_dict[attacker_asn].policy.__class__ = OgPolicyCls

            if OgPolicyCls != self.scenario_config.BasePolicyCls:
                non_default[attacker_asn] = OgPolicyCls
            else:
                del non_default[attacker_asn]

        self.non_default_asn_cls_dict = frozendict(non_default)

    def _generate_policy_cls(self, PolicyCls: type["Policy"]) -> type["Policy"]:
        """Generates the Spoofing Didsconnecting Attacker policy class

        This is a dynamic subclass of the attacker's class
        """

        class SpoofingDisconnectingAttacker(PolicyCls):
            name = "Spoofing disconnecting attacker"

            def _policy_propagate(
                self,
                neighbor: "AS",
                ann: "Ann",
                propagate_to: Relationships,
                send_rels: set[Relationships],
            ) -> bool:
                if ann.recv_relationship.value == Relationships.ORIGIN.value:
                    ann = ann.copy({"next_hop_asn": neighbor.asn})
                    self._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)
                    return True
                else:
                    return False

        return SpoofingDisconnectingAttacker
