from collections import defaultdict

from lib_caida_collector import AS

from .ann_containers import LocalRib
from .ann_containers import RIBIn, RibsOut
from .ann_containers import SendQueue, RecvQueue
from ..enums import Relationships
from ..announcement import Announcement as Ann
from .bgp_policy import BGPPolicy


class BGPRIBSPolicy(BGPPolicy):
    __slots__ = ["rib_in", "ribs_out", "recv_q", "send_q", "local_rib"]

    def __init__(self, *args, **kwargs):
        self.local_rib = LocalRib()
        # Ribs in contains unprocessed anns, unchanged from previous AS
        self.rib_in = RIBIn()
        self.ribs_out = RibsOut()
        self.recv_q = RecvQueue()
        self.send_q = SendQueue()

    def _propagate(policy_self, self, propagate_to: Relationships, send_rels: list):
        """Propogates announcements to other ASes

        send_rels is the relationships that are acceptable to send
        """
        # _policy_propagate and _add_ann_to_q have been overriden
        # So that instead of propagating, announcements end up in the send_q
        # Send q contains both announcements and withdrawals
        policy_self._populate_send_q(self, propagate_to, send_rels)

        # Send announcements/withdrawals and add to ribs out
        policy_self._send_anns(self, propagate_to)

    def _populate_send_q(policy_self, self, propagate_to, send_rels):
        return super(BGPRIBSPolicy, policy_self)._propagate(self, propagate_to, send_rels)

    def _policy_propagate(policy_self, self, propagate_to, send_rels, ann, as_obj):
        """Don't send what we've already sent"""

        ribs_out_ann = policy_self.ribs_out[as_obj.asn].get(ann.prefix)
        return ann.prefix_path_attributes_eq(ribs_out_ann)

    def _add_ann_to_q(policy_self, self, as_obj, ann, propagate_to, send_rels):
        policy_self.send_q.add_ann(as_obj.asn, ann)

    def _send_anns(policy_self, self, propagate_to: Relationships):
        """Sends announcements and populates ribs out"""

        neighbor_prefix_anns = policy_self.send_q.neighbor_prefix_anns(neighbors=getattr(self, propagate_to.name.lower()))

        for (neighbor_obj, prefix, ann) in neighbor_prefix_anns:
            neighbor_obj.policy.recv_q.add_ann(ann, prefix=prefix)
            # Update Ribs out if it's not a withdraw
            if not ann.withdraw:
               policy_self.ribs_out[neighbor_obj.asn][prefix] = ann
        for neighbor_obj in getattr(self, propagate_to.name.lower()):
            policy_self.send_q.reset_neighbor(neighbor_obj.asn)

    def process_incoming_anns(policy_self,
                              self,
                              recv_relationship: Relationships,
                              *args,
                              propagation_round=None,
                              # Usually None for attack
                              attack=None,
                              reset_q=True,
                              **kwargs):
        """Process all announcements that were incoming from a specific rel"""

        for prefix, ann_list in policy_self.recv_q.prefix_anns():

            # Get announcement currently in local rib
            local_rib_ann = policy_self.local_rib.get_ann(prefix)
            current_best_ann = local_rib_ann
            current_best_ann_processed = True

            # Announcement will never be overriden, so continue
            if current_best_ann is not None and current_best_ann.seed_asn is not None:
                continue

            # For each announcement that is incoming
            for ann in ann_list:
                # withdrawals
                err = "Recieved two withdrawals from the same neighbor"
                assert len([x.as_path[0] for x in ann_list if x.withdraw]) == len(set([x.as_path[0] for x in ann_list if x.withdraw])), err

                err = "Recieved two NON withdrawals from the same neighbor"
                assert len([x.as_path[0] for x in ann_list if not x.withdraw]) == len(set([x.as_path[0] for x in ann_list if not x.withdraw])), err

               # Always add to ribs in if it's not a withdrawal
                if not ann.withdraw:
                    try:
                        err = "you should never be replacing anns. You should always withdraw first, have it be blank, then add the new one"
                        assert policy_self.rib_in.get_unprocessed_ann_recv_rel(ann.as_path[0], prefix) is None, err
                    except:
                        print("Incoming anns")
                        for ann in ann_list:
                            print(ann, ann.withdraw)
                        __ann, rel = (policy_self.rib_in.get_unprocessed_ann(ann.as_path[0], prefix))
                        print("RIBS IN", str(__ann), rel)
                        input("ERROR!!!! fix this later with better error checking")
                        raise NotImplementedError

                    policy_self.rib_in.add_unprocessed_ann(ann.as_path[0], ann, recv_relationship, prefix=prefix)

                # If it's valid, process it
                if policy_self._valid_ann(self, ann, recv_relationship):
                    if ann.withdraw:
                        policy_self._process_incoming_withdrawal(self, ann, ann.as_path[0], ann.prefix, recv_relationship)

                    else:
                        new_ann_is_better = policy_self._new_ann_is_better(self,
                                                                           current_best_ann,
                                                                           current_best_ann_processed,
                                                                           recv_relationship,
                                                                           ann,
                                                                           False,
                                                                           recv_relationship)
                        # If the new priority is higher
                        if new_ann_is_better:
                            current_best_ann = ann
                            current_best_ann_processed = False

            if local_rib_ann is not None and current_best_ann_processed is False:
                # Best ann has already been processed
                withdraw_ann = local_rib_ann.copy(withdraw=True)
                policy_self._withdraw_ann_from_neighbors(self, withdraw_ann)
                err = "withdrawing an announcement that is identical to new ann"
                assert not withdraw_ann.prefix_path_attributes_eq(policy_self._deep_copy_ann(self, ann, recv_relationship)), err

            # We have a new best!
            if current_best_ann_processed is False:
                current_best_ann = policy_self._deep_copy_ann(self, ann, recv_relationship)
                # Save to local rib
                policy_self.local_rib.add_ann(current_best_ann, prefix=prefix)

        policy_self._reset_q(reset_q)

    def _process_incoming_withdrawal(policy_self, self, ann, neighbor, prefix,
                                     recv_relationship):

        # Return if the current ann was seeded (for an attack)
        local_rib_ann = policy_self.local_rib.get_ann(prefix)
        assert not ((local_rib_ann is not None) and ((ann.prefix_path_attributes_eq(local_rib_ann)) and (local_rib_ann.seed_asn is not None))), f"Trying to withdraw a seeded ann {local_rib_ann.seed_asn}"


        current_ann_rib_in, _ = policy_self.rib_in.get_unprocessed_ann_recv_rel(neighbor, prefix)
        err = f"Cannot withdraw ann that was never sent.\n\t Ribs in: {current_ann_rib_in}\n\t withdraw: {ann}"
        assert ann.prefix_path_attributes_eq(current_ann_rib_in), err
        
        # Remove ann from Ribs in
        policy_self.rib_in.remove_entry(neighbor, prefix)

        # Remove ann from local rib
        withdraw_ann = policy_self._deep_copy_ann(self, ann, recv_relationship, withdraw=True)
        if withdraw_ann.prefix_path_attributes_eq(policy_self.local_rib.get_ann(prefix)):
            policy_self.local_rib.remove_ann(prefix)
            # Also remove from neighbors
            policy_self._withdraw_ann_from_neighbors(self, withdraw_ann)

        best_ann = policy_self._select_best_rib_in(self, prefix)
        
        # Put new ann in local rib
        if best_ann is not None:
            policy_self.local_rib.add_ann(best_ann, prefix=prefix)

        err = "Best ann should not be identical to the one we just withdrew"
        assert not withdraw_ann.prefix_path_attributes_eq(best_ann), err

    def _withdraw_ann_from_neighbors(policy_self, self, withdraw_ann):
        """Withdraw a route from all neighbors.

        This function will not remove an announcement from the local rib, that
        should be done before calling this function.

        Note that withdraw_ann is a deep copied ann
        """
        assert withdraw_ann.withdraw is True
        # Check ribs_out to see where the withdrawn ann was sent
        for send_neighbor, inner_dict in policy_self.ribs_out.items():
            # If the two announcements are equal
            if withdraw_ann.prefix_path_attributes_eq(inner_dict.get(withdraw_ann.prefix)):
                # Delete ann from ribs out
                del policy_self.ribs_out[send_neighbor][withdraw_ann.prefix]
                policy_self.send_q.add_ann(send_neighbor, withdraw_ann)

        # We may not have sent the ann yet, it may just be in the send queue and not ribs out
        # We want to cancel out any anns in the send_queue that match the withdrawal
        for neighbor_obj in self.peers + self.customers + self.providers:
            send_info = policy_self.send_q.get_send_info(neighbor_obj, withdraw_ann.prefix)
            if send_info is None or send_info.ann is None:
                continue
            elif send_info.ann.prefix_path_attributes_eq(withdraw_ann):
                send_info.ann = None
            
    def _select_best_rib_in(policy_self, self, prefix):
        """Selects best ann from ribs in. Remember, ribs in anns are NOT deep copied"""

        # Get the best announcement
        best_unprocessed_ann = None
        best_recv_relationship = None
        for new_unprocessed_ann, new_recv_relationship in policy_self.rib_in.get_ann_infos(prefix):
            if policy_self._new_ann_is_better(self,
                                              best_unprocessed_ann,
                                              False,
                                              best_recv_relationship,
                                              new_unprocessed_ann,
                                              False,
                                              new_recv_relationship):
                best_unprocessed_ann = new_unprocessed_ann
                best_recv_relationship = new_recv_relationship

        if best_unprocessed_ann is not None:
            return policy_self._deep_copy_ann(self, best_unprocessed_ann, best_recv_relationship)
        else:
            return None
