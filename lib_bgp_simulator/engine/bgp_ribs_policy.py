from copy import deepcopy

from lib_caida_collector import AS

from .local_rib import LocalRib
from .ann_queues import SendQueue, RecvQueue
from .relationships import Relationships
from ..announcement import Announcement as Ann
from .bgp_policy import BGPPolicy


class BGPRIBSPolicy(BGPPolicy):
    __slots__ = []

    def _propagate(policy_self, self, propagate_to: Relationships, send_rels: list):
        """Propogates announcements from local rib to other ASes

        send_rels is the relationships that are acceptable to send
        """

        for as_obj in getattr(self, propagate_to.name.lower()):
            for prefix, ann in self.local_rib.items():
                if ann.recv_relationship in send_rels:
                    # Update RIBs out
                        if ann not in self.ribs_out[as_obj.asn][prefix]:
                            self.ribs_out[as_obj.asn][prefix].append(ann)
                            self.send_q[as_obj.asn][prefix].append(ann)

            # Send everything in the send queues
            for prefix, anns in self.send_q[as_obj.asn].items():
                for ann in anns:
                    as_obj.recv_q[self.asn][prefix].append(ann)

    def process_incoming_anns(policy_self, self, recv_relationship: Relationships,
        recv_q=None, limit_prefix=None):
        """Process all announcements that were incoming from a specific rel"""

        if recv_q is None:
            recv_q = self.recv_q

        for neighbor, value in recv_q.items():
            for prefix, ann_list in value.items():
                if limit_prefix is not None and limit_prefix != prefix:
                    # limit_prefix allows limiting processing to a specific prefix
                    continue
                # Get announcement currently in local rib
                og_best_ann = self.local_rib.get(prefix)
                best_ann = og_best_ann
                # Done here to optimize
                if best_ann is not None and best_ann.seed_asn is not None:
                    continue
                if best_ann is None:
                    best_priority = -1
                else:
                    best_priority = best_ann.priority

                possible_replace = (True if best_ann is None else 
                    best_ann.recv_relationship <= recv_relationship)
                # For each announcement that was incoming
                for ann in ann_list:
                    if not ann in self.ribs_in[neighbor][prefix]:
                        # If never seen before, copy to ribs_in
                        self.ribs_in[neighbor][prefix].append(ann)
                        if ann.withdraw:
                            # Remove withdrawn routes
                            ann_to_remove = deepcopy(ann)
                            ann_to_remove.withdraw = False
                            self.ribs_in[neighbor][prefix].remove(ann_to_remove)
                            # Update AS path for loc_rib and ribs_out
                            ann_to_remove.as_path = (self.asn, *ann.as_path)
                            self.loc_rib[prefix].remove(ann_to_remove)
                            for send_neighbor in self.ribs_out:
                                if ann_to_remove in self.ribs_out[send_neighbor][prefix]:
                                    if ann_to_remove in self.send_q[send_neighbor][prefix]:
                                        # If the withdrawn route has not been sent to the send_neighbor yet, don't send it
                                        self.send_q[send_neighbor][prefix].remove(ann_to_remove)
                                    else:
                                        # Otherwise propagate the withdrawal
                                        withdraw = deepcopy(ann_to_remove)
                                        withdraw.withdraw = True
                                        self.send_q[send_neighbor][prefix].append(withdraw)
                                    self.ribs_out[send_neighbor][prefix].remove(ann_to_remove)
                            self.loc_rib[prefix] = policy_self.process_incoming_anns(self, recv_relationship, 
                                recv_q=self.ribs_in, limit_prefix=prefix)

                        elif possible_replace:
                            priority = policy_self._get_priority(ann, recv_relationship)
                            # If the new priority is higher
                            if priority > best_priority:
                                # Save the priority and announcement for later
                                # We don't copy the ann here, since we might find another better ann later
                                best_priority = priority
                                best_ann = ann

                # If it did not change
                if best_ann is og_best_ann:
                    continue
                else:
                    # Don't bother tiebreaking, if priority is same, keep existing
                    # Just like normal BGP
                    # Tiebreaking with time and such should go into the priority
                    # If we ever decide to do that
                    best_ann = deepcopy(best_ann)
                    best_ann.seed_asn = None
                    best_ann.as_path = (self.asn, *ann.as_path)
                    best_ann.recv_relationship = recv_relationship
                    best_ann.priority = best_priority
                    # Save to local rib
                    self.local_rib[prefix] = best_ann
                    # Update RIBs out, remove old announcement only
                    for neighbor, value in self.ribs_out.items():
                        for prefix, ann in value.items():
                            if og_best_ann in self.ribs_out[neighbor][prefix]:
                                    if ann_to_remove in self.send_q[neighbor][prefix]:
                                        # If the withdrawn route has not been sent to the send_neighbor yet, don't send it
                                        self.send_q[neighbor][prefix].remove(og_best_ann)
                                    else:
                                        # Otherwise propagate the withdrawal
                                        # Withdrawal is guaranteed to be propagated before the new best ann
                                        withdraw = deepcopy(og_best_ann)
                                        withdraw.withdraw = True
                                        self.send_q[neighbor][prefix].append(withdraw)

        if recv_q == self.recv_q and limit_prefix is None:
            # If this is the normal processing of announcements, reset the recv_q
            self.recv_q = RecvQueue()

