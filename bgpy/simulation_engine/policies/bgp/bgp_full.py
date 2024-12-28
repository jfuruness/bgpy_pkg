from typing import TYPE_CHECKING
from warnings import warn

from bgpy.shared.enums import Relationships
from bgpy.simulation_engine.ann_containers import RIBsIn, RIBsOut
from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine.announcement import Announcement as Ann
    from bgpy.simulation_framework import Scenario


class BGPFull(BGP):
    name = "BGP Full"

    def __init__(
        self,
        *args,
        ribs_in: RIBsIn | None = None,
        ribs_out: RIBsOut | None = None,
        **kwargs,
    ):
        super(BGPFull, self).__init__(*args, **kwargs)
        self.ribs_in: RIBsIn = ribs_in if ribs_in else RIBsIn()
        self.ribs_out: RIBsOut = ribs_out if ribs_out else RIBsOut()

    #########################
    # Process incoming anns #
    #########################

    def process_incoming_anns(
        self: "BGPFull",
        *,
        from_rel: "Relationships",
        propagation_round: int,
        # Usually None for attack
        scenario: "Scenario",
        reset_q: bool = True,
    ):
        """Process all announcements that were incoming from a specific rel"""

        for prefix, ann_list in self.recv_q.items():
            # Get announcement currently in local rib
            local_rib_ann: Ann | None = self.local_rib.get(prefix)
            og_ann = local_rib_ann

            # For each announcement that is incoming
            for new_ann in ann_list:
                # Validation funcs
                assert self.only_one_withdrawal_per_prefix_per_neighbor(ann_list)
                assert self.only_one_ann_per_prefix_per_neighbor(ann_list)

                # If withdrawal remove from RIBsIn, otherwise add to RIBsIn
                self._process_new_ann_in_ribs_in(new_ann, prefix, from_rel)

                # Process withdrawals even for invalid anns in the ribs_in
                if new_ann.withdraw:
                    local_rib_ann = self._remove_from_local_rib_and_get_new_best_ann(
                        new_ann, local_rib_ann
                    )
                else:
                    local_rib_ann = self._get_new_best_ann(
                        local_rib_ann, new_ann, from_rel
                    )

            if og_ann != local_rib_ann:
                if local_rib_ann:
                    self.local_rib.add_ann(local_rib_ann)
                if og_ann:
                    self.withdraw_ann_from_neighbors(
                        og_ann.copy(
                            {
                                "next_hop_asn": self.as_.asn,
                                "withdraw": True,
                            }
                        )
                    )

        self._reset_q(reset_q)

    def _process_new_ann_in_ribs_in(
        self, unprocessed_ann: "Ann", prefix: str, from_rel: Relationships
    ) -> None:
        """Adds ann to ribs in if the ann is not a withdrawal"""

        # Remove ann using withdrawal from RIBsIn
        if unprocessed_ann.withdraw:
            neighbor = unprocessed_ann.as_path[0]
            # Remove ann from Ribs in
            self.ribs_in.remove_entry(neighbor, prefix, self.error_on_invalid_routes)
        # Add ann to RIBsIn
        else:
            assert self.no_implicit_withdrawals(unprocessed_ann, prefix)
            self.ribs_in.add_unprocessed_ann(unprocessed_ann, from_rel)

    def _remove_from_local_rib_and_get_new_best_ann(
        self, new_ann: "Ann", local_rib_ann: "Ann | None"
    ) -> "Ann | None":
        # This is for removing the original local RIB ann
        if (
            local_rib_ann
            and new_ann.prefix == local_rib_ann.prefix
            # new_ann is unproccessed
            and new_ann.as_path == local_rib_ann.as_path[1:]
            and local_rib_ann.recv_relationship != Relationships.ORIGIN
        ):
            # Withdrawal exists in the local RIB, so remove it and reset current ann
            self.local_rib.pop(new_ann.prefix, None)
            local_rib_ann = None
            # Get the new best ann thus far
            processed_best_ribs_in_ann = self._get_and_process_best_ribs_in_ann(
                new_ann.prefix
            )
            if processed_best_ribs_in_ann:
                local_rib_ann = self._get_best_ann_by_gao_rexford(
                    local_rib_ann,
                    processed_best_ribs_in_ann,
                )

        return local_rib_ann

    def withdraw_ann_from_neighbors(self: "BGPFull", withdraw_ann: "Ann") -> None:
        """Withdraw a route from all neighbors.

        This function will not remove an announcement from the local rib, that
        should be done before calling this function.

        Note that withdraw_ann is a deep copied ann
        """
        assert withdraw_ann.withdraw is True
        assert withdraw_ann.next_hop_asn == self.as_.asn
        # Check ribs_out to see where the withdrawn ann was sent
        for send_neighbor_asn in self.ribs_out.neighbors():
            # Delete ann from ribs out
            removed = self.ribs_out.remove_entry(send_neighbor_asn, withdraw_ann.prefix)
            # If the announcement was sent to that neighbor
            if removed:
                send_rels = set(Relationships)
                if send_neighbor_asn in self.as_.customer_asns:
                    propagate_to = Relationships.CUSTOMERS
                elif send_neighbor_asn in self.as_.provider_asns:
                    propagate_to = Relationships.PROVIDERS
                elif send_neighbor_asn in self.as_.peer_asns:
                    propagate_to = Relationships.PEERS
                else:
                    raise NotImplementedError("Case not accounted for")
                send_neighbor = self.as_.as_graph.as_dict[send_neighbor_asn]
                # Policy took care of it's own propagation for this ann
                if self._policy_propagate(
                    send_neighbor, withdraw_ann, propagate_to, send_rels
                ):
                    continue
                else:
                    self._process_outgoing_ann(
                        send_neighbor, withdraw_ann, propagate_to, send_rels
                    )

    def _get_and_process_best_ribs_in_ann(self: "BGPFull", prefix: str) -> "Ann | None":
        """Selects best ann from ribs in (remember, RIBsIn is unprocessed"""

        # Get the best announcement
        best_ann: Ann | None = None
        for ann_info in self.ribs_in.get_ann_infos(prefix):
            # This also processes the announcement
            best_ann = self._get_new_best_ann(
                best_ann, ann_info.unprocessed_ann, ann_info.recv_relationship
            )
        return best_ann

    ###################
    # Propagate funcs #
    ###################

    def _prev_sent(self: "BGPFull", neighbor: "AS", ann: "Ann") -> bool:
        """Don't send what we've already sent

        NOTE: I think this may not be functioning properly, this seems
        to always return False even when it shouldn't...

        But at least that won't affect results, just bad performance for
        a very niche case
        """

        return ann == self.ribs_out.get_ann(neighbor.asn, ann.prefix)

    def _process_outgoing_ann(
        self: "BGPFull",
        neighbor: "AS",
        ann: "Ann",
        propagate_to,
        send_rels: set["Relationships"],
    ):
        if not ann.withdraw:
            self.ribs_out.add_ann(neighbor.asn, ann)

        super()._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)

    ##############
    # YAML funcs #
    ##############

    def __to_yaml_dict__(self):
        """This optional method is called when you call yaml.dump()"""

        as_dict = super(BGPFull, self).__to_yaml_dict__()
        as_dict.update({"ribs_in": self.ribs_in, "ribs_out": self.ribs_out})
        return as_dict

    ###################################################################################
    # Everything below this point doesn't matter for 90% of development with BGPFull  #
    ###################################################################################

    ####################
    # Validation Funcs #
    ####################

    # By default this is true, since most often invalid withdrawals are development
    # mistakes. However, withdrawals can be used as attack vectors, so I've added this
    error_on_invalid_routes = True

    # NOTE: For all validation funcs, we assert, but also return True
    # this way, in the code that calls this function, we can call these with assert
    # so that they get ignored when run with pypy3 -O to ignore the overhead
    # of the function calls, but we don't need to clutter the main code with the msg

    def only_one_withdrawal_per_prefix_per_neighbor(self, anns: list["Ann"]) -> bool:
        """Ensures that neighbor didn't send two withdrawals for same prefix"""
        assert not (
            len([x.as_path[0] for x in anns if x.withdraw])
            != len({x.as_path[0] for x in anns if x.withdraw})
            and self.error_on_invalid_routes
        ), f"More than one withdrawal per prefix from the same neighbor {anns}"
        return True

    def only_one_ann_per_prefix_per_neighbor(self, anns: list["Ann"]) -> bool:
        """Ensures that neighbor didn't send two anns for same prefix"""

        err = (
            f"{self.as_.asn} Recieved two NON withdrawals "
            f"from the same neighbor {anns}"
        )
        assert not (
            len([(x.as_path[0], x.next_hop_asn) for x in anns if not x.withdraw])
            != len({(x.as_path[0], x.next_hop_asn) for x in anns if not x.withdraw})
            and self.error_on_invalid_routes
        ), err
        return True

    def no_implicit_withdrawals(self, ann: "Ann", prefix: str) -> bool:
        """Ensures that you withdraw, then add a new ann

        Ensures that no ann is overwritten by another ann, anns can only be
        overwritten by withdrawals
        """

        ribs_in_ann = self.ribs_in.get_unprocessed_ann_recv_rel(ann.as_path[0], prefix)
        err = (
            f"Ann {ann} overwrote RIBsIn ann {ribs_in_ann} at AS {self.as_.asn}. "
            "You must withdraw first, then add new ann"
        )
        assert ribs_in_ann is None or not self.error_on_invalid_routes, err
        return True

    ####################
    # Deprecated funcs #
    ####################

    @property
    def _ribs_in(self) -> RIBsIn:
        warn(
            "Please use .ribs_in instead of ._ribs_in. "
            "This will be removed in a later version",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.ribs_in

    @property
    def _ribs_out(self) -> RIBsOut:
        warn(
            "Please use .ribs_out instead of ._ribs_out. "
            "This will be removed in a later version",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.ribs_out

    def prep_withdrawal_for_next_propagation(self, prefix: str) -> None:
        """Removes a prefix from the local RIB and withdraws it next propagation"""

        warn(
            "Now that I've refactored the withdrawals "
            "prep_withdrawal_for_next_propagation no longer "
            "makes sense and is deprecated since it doesn't deal with RIBsIn "
            "even though the name deceptively implies that it does. Please use: "
            " withdraw_ann = self.local_rib.pop(prefix).copy({'withdraw': True}); "
            "self.withdraw_ann_from_neighbors(withdraw_ann); "
            "This will be removed in a later version",
            category=DeprecationWarning,
            stacklevel=2,
        )

        # Create withdraw ann and remove the og from local rib
        withdraw_ann = self.local_rib.pop(prefix).copy({"withdraw": True})
        self.withdraw_ann_from_neighbors(withdraw_ann)
