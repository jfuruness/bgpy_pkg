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

    def process_incoming_anns(policy_self, self, recv_relationship: Relationships):
        """Process all announcements that were incoming from a specific rel"""

        for neighbor, value in self.recv_q.items():
            for prefix, ann_list in value.items():
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

                # TODO WITHDRAWALS
                possible_replace = True if best_ann is None else best_ann.recv_relationship <= recv_relationship
                # For each announcement that was incoming
                for ann in ann_list:
                    if not ann in self.ribs_in[neighbor][prefix]:
                        # If never seen before, copy to ribs_in
                        self.ribs_in[neighbor][prefix].append(ann)
                        if possible_replace:
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
                            if og_best_ann in self.ribs_out[as_obj.asn][prefix]:
                                self.ribs_out[as_obj.asn][prefix].remove(og_best_ann)
                                # Withdrawal is guaranteed to be propagated before the new best ann
                                withdraw = deepcopy(og_best_ann)
                                withdraw.withdraw = True
                                self.send_q[as_obj.asn][prefix].append(withdraw)

        self.recv_q = RecvQueue()

