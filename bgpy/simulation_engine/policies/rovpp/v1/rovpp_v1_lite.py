from typing import TYPE_CHECKING, Iterator

from bgpy.shared.enums import Relationships, Timestamps
from bgpy.simulation_engine.policies.rov import ROV

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_framework import Scenario


class ROVPPV1Lite(ROV):
    """An Policy that deploys ROV++V1 Lite as defined in the ROV++ paper

    ROV++ Improved Deployable Defense against BGP Hijacking
    """

    name: str = "ROV++V1 Lite"

    def _policy_propagate(
        self,
        neighbor: "AS",
        ann: "Ann",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> bool:
        """Only propagate announcements that aren't blackholes"""

        # Policy handled this ann for propagation (and did nothing if blackhole)
        return ann.rovpp_blackhole

    def process_incoming_anns(
        self,
        *,
        from_rel: Relationships,
        propagation_round: int,
        scenario: "Scenario",
        reset_q: bool = True,
    ) -> None:
        """Processes all incoming announcements from a specific rel"""

        super().process_incoming_anns(
            from_rel=from_rel,
            propagation_round=propagation_round,
            scenario=scenario,
            reset_q=False,
        )
        self._add_blackholes(from_rel, scenario)

        # It's possible that we had a previously valid prefix
        # Then later recieved a subprefix that was invalid
        # So we must recount the holes of each ann in local RIB
        self._recount_holes(propagation_round)

        self._reset_q(reset_q)

    def _add_blackholes(self, from_rel: "Relationships", scenario: "Scenario") -> None:
        """Adds blackhole announcements to the local RIB

        First add all non routed prefixes from ROAs as blackholes
        Then for each ann in the local RIB, if you received an
        invalid subprefix from the same neighbor,
        add it to the local RIB as a blackhole
        """

        non_routed_blackholes = self._get_non_routed_blackholes_to_add(scenario)
        routed_blackholes = self._get_routed_blackholes_to_add(from_rel, scenario)
        self._add_blackholes_tolocal_rib(non_routed_blackholes + routed_blackholes)

    def _get_non_routed_blackholes_to_add(
        self, scenario: "Scenario"
    ) -> tuple["Ann", ...]:
        """Get all the bholes for non routed prefixes to prevent superprefix attacks"""

        non_routed_blackholes_to_add = list()
        for roa in scenario.roas:
            # ROA is non routed
            if roa.is_non_routed:
                blackhole_ann = scenario.scenario_config.AnnCls(
                    prefix=str(roa.prefix),
                    next_hop_asn=self.as_.asn,
                    as_path=(self.as_.asn,),
                    timestamp=Timestamps.VICTIM.value,
                    seed_asn=None,
                    recv_relationship=Relationships.ORIGIN,
                    rovpp_blackhole=True,
                )
                non_routed_blackholes_to_add.append(blackhole_ann)
        return tuple(non_routed_blackholes_to_add)

    def _get_routed_blackholes_to_add(
        self, from_rel: "Relationships", scenario: "Scenario"
    ) -> tuple["Ann", ...]:
        """Get all the bholes from the anns you just recieved"""

        blackholes_to_add = list()
        # Then add blackholes for anns in local RIB when you've
        # recieved an invalid subprefix from the same neighbor
        for _, ann in self.local_rib.items():
            for sub_ann in self._invalid_subprefixes_from_same_neighbor(scenario, ann):
                blackhole = self._copy_and_process(
                    sub_ann,
                    from_rel,
                    overwrite_default_kwargs={
                        "next_hop_asn": self.as_.asn,
                        "rovpp_blackhole": True,
                    },
                )
                blackholes_to_add.append(blackhole)
        return tuple(blackholes_to_add)

    def _invalid_subprefixes_from_same_neighbor(
        self, scenario: "Scenario", ann: "Ann"
    ) -> Iterator["Ann"]:
        """Returns all invalid subprefixes of announcement from the same neighbor"""

        # If we are the origin, then there are zero invalid anns from the same neighbor
        if ann.recv_relationship == Relationships.ORIGIN:
            return ()  # type: ignore
        # For each subprefix in this scenario of the prefix within the local RIB
        for subprefix in scenario.ordered_prefix_subprefix_dict[ann.prefix]:
            # For each subprefix ann that was recieved
            # NOTE: these wouldn't be in the local RIB since they're invalid
            # and dropped by default (but they are recieved so we can check there)
            for sub_ann in self.recv_q.get_ann_list(subprefix):
                # Holes are only from same neighbor
                if (
                    self.ann_is_invalid_by_roa(sub_ann)
                    # Check the first one in the path since it's already processed
                    and sub_ann.as_path[0] == ann.as_path[1]
                ):
                    yield sub_ann

    def _add_blackholes_tolocal_rib(self, blackholes: tuple["Ann", ...]) -> None:
        """Adds all blackholes to the local RIB"""

        for blackhole in blackholes:
            existing_ann = self.local_rib.get(blackhole.prefix)
            # Don't overwrite valid existing announcements
            if existing_ann is None or self.ann_is_invalid_by_roa(existing_ann):
                self.local_rib.add_ann(blackhole)

    def _recount_holes(self, propagation_round: int) -> None:
        # It's possible that we had a previously valid prefix
        # Then later recieved a subprefix that was invalid
        # Or there was previously an invalid subprefix
        # But later that invalid subprefix was removed
        # So we must recount the holes of each ann in local RIB
        # NOTE June 22 2024: I think doing this may require the use of the RIBsIn
        # because you could recieve a subprefix hijack round 1, and round 2 receive
        # the valid prefix from the same neighbor
        # not going to implement because of that, and because I don't think there's
        # a need to, because as far as I know there aren't any two round attacks
        # against ROV++. If someone comes up with one let me know and I can try to
        # help out, email at jfuruness@gmail.com.
        # NOTE: Additionally, we don't account for withdrawals at all...
        if propagation_round != 0:
            raise NotImplementedError("TODO: support ROV++ for multiple rounds")
