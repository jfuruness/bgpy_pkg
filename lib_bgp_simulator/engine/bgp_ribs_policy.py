from copy import deepcopy

from lib_caida_collector import AS

from .local_rib import LocalRib
from .ribs import RibsIn, RibsOut
from .ann_queues import SendQueue, RecvQueue
from ..enums import Relationships
from ..announcement import Announcement as Ann
from .bgp_policy import BGPPolicy


class BGPRIBSPolicy(BGPPolicy):
    __slots__ = ["ribs_in", "ribs_out", "recv_q", "send_q", "local_rib"]

    def __init__(self, *args, **kwargs):
        self.local_rib = LocalRib()
        # Ribs in contains unprocessed anns, unchanged from previous AS
        self.ribs_in = RibsIn()
        self.ribs_out = RibsOut()
        self.recv_q = RecvQueue()
        self.send_q = SendQueue()

    def _propagate(policy_self, self, propagate_to: Relationships, send_rels: list):
        """Propogates announcements to other ASes

        send_rels is the relationships that are acceptable to send
        """

        # Populate the send queue, which might have anns and withdrawals
        policy_self._populate_send_q(self, propagate_to, send_rels)
        # Send announcements/withdrawals and add to ribs out
        policy_self._send_anns(self, propagate_to)

    def _populate_send_q(policy_self, self, propagate_to, send_rels):
        """Populates send queue and ribs out"""

        for as_obj in getattr(self, propagate_to.name.lower()):
            for prefix, ann in policy_self.local_rib.items():
                if ann.recv_relationship in send_rels:
                    ribs_out_ann = policy_self.ribs_out[as_obj.asn].get(prefix)
                    # To make sure we don't repropagate anns we have already sent
                    if not ann.prefix_path_attributes_eq(ribs_out_ann):
                        policy_self.send_q[as_obj.asn][prefix].append(ann)

    def _send_anns(policy_self, self, propagate_to: Relationships):
        """Sends announcements and populates ribs out"""

        for as_obj in getattr(self, propagate_to.name.lower()):
            # Send everything in the send queues
            for prefix, anns in policy_self.send_q[as_obj.asn].items():
                assert len(anns) <= 2, "Shouldn't have more than an ann and withdrawal"
                for ann in anns:
                    as_obj.policy.recv_q[self.asn][prefix].append(ann)
                    # Update Ribs out if it's not a withdraw
                    if not ann.withdraw:
                        policy_self.ribs_out[as_obj.asn][prefix] = ann
            policy_self.send_q[as_obj.asn] = []

    def process_incoming_anns(policy_self, self, recv_relationship: Relationships):
        """Process all announcements that were incoming from a specific rel"""

        for neighbor, inner_dict in policy_self.recv_q.items():
            for prefix, ann_list in inner_dict.items():

                # Get announcement currently in local rib
                local_rib_ann = policy_self.local_rib.get(prefix)
                best_ann = local_rib_ann

                # Announcement will never be overriden, so continue
                if best_ann is not None and best_ann.seed_asn is not None:
                    continue

                # For each announcement that is incoming
                for ann in ann_list:
                    if ann.withdraw:
                        policy_self._process_incoming_withdrawal(self, ann, neighbor, ann.prefix, recv_relationship)

                    else:
                        # BGP Loop Prevention Check
                        if self.asn in ann.as_path:
                            continue

                        policy_self.ribs_in[neighbor][prefix] = (ann, recv_relationship)

                        new_ann_is_better = policy_self._new_ann_is_better(self, best_ann, ann, recv_relationship)
                        # If the new priority is higher
                        if new_ann_is_better:
                            if best_ann is not None:
                                withdraw_ann = deepcopy(best_ann)
                                withdraw_ann.withdraw = True
                                policy_self._withdraw_ann_from_neighbors(self, withdraw_ann)
                            best_ann = policy_self._deep_copy_ann(self, ann, recv_relationship)
                            # Save to local rib
                            policy_self.local_rib[prefix] = best_ann

        # If this is the normal processing of announcements, reset the recv_q
        policy_self.recv_q = RecvQueue()

    def _process_incoming_withdrawal(policy_self, self, ann, neighbor, prefix,
                                     recv_relationship):

        # Return if the current ann was seeded (for an attack)
        local_rib_ann = policy_self.local_rib.get(prefix)
        if (local_rib_ann is not None and
            ann.prefix_path_attributes_eq(local_rib_ann) and
            local_rib_ann.seed_asn is not None):
            return

        current_ann_ribs_in, _ = policy_self.ribs_in[neighbor][prefix]
        assert ann.prefix_path_attributes_eq(current_ann_ribs_in)
        
        # Remove ann from Ribs in
        del policy_self.ribs_in[neighbor][prefix]

        # Remove ann from local rib
        withdraw_ann = policy_self._deep_copy_ann(self, ann, recv_relationship)
        if withdraw_ann.prefix_path_attributes_eq(policy_self.local_rib.get(prefix)):
            del policy_self.local_rib[prefix]
            # Also remove from neighbors
            policy_self._withdraw_ann_from_neighbors(self, withdraw_ann)

        best_ann = policy_self._select_best_ribs_in(self, prefix)
        
        # Put new ann in local rib
        if best_ann is not None:
            policy_self.local_rib[prefix] = best_ann

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
                # If the ann being withdrawn has not been sent yet, remove it
                # from the send_q and do not send the withdrawal. 
                found_in_send_q = False
                for i, ann in enumerate(policy_self.send_q[send_neighbor][withdraw_ann.prefix]):
                    if withdraw_ann.prefix_path_attributes_eq(ann) and not ann.withdraw:
                        policy_self.send_q[send_neighbor][withdraw_ann.prefix].pop(i)
                        found_in_send_q = True
                # Add withdrawal to send queue
                if not found_in_send_q:
                    policy_self.send_q[send_neighbor][withdraw_ann.prefix].append(withdraw_ann)

        # Now re-check the send_q for any that have not been sent yet
        for send_neighbor, inner_dict in policy_self.send_q.items():
            for i, ann in enumerate(inner_dict.get(withdraw_ann.prefix)):
                if withdraw_ann.prefix_path_attributes_eq(ann) and not ann.withdraw:
                    policy_self.send_q[send_neighbor][withdraw_ann.prefix].pop(i)
 
    def _select_best_ribs_in(policy_self, self, prefix):
        """Selects best ann from ribs in. Remember, ribs in anns are NOT deep copied"""

        ann_list = []
        for neighbor, inner_dict in policy_self.ribs_in.items():
            if prefix in inner_dict:
                ann_list.append(inner_dict[prefix])

        if len(ann_list) == 0:
            return None
        else:
            # Get the best announcement
            best_ann = None
            for ann, recv_relationship in ann_list:
                if policy_self._new_ann_is_better(self, best_ann, ann, recv_relationship):
                    best_ann = policy_self._deep_copy_ann(self, ann, recv_relationship)

            return best_ann
