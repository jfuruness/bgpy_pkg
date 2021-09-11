from copy import deepcopy

from lib_caida_collector import AS

from .local_rib import LocalRib
from .ribs import RibsIn, RibsOut
from .ann_queues import SendQueue, RecvQueue
from ..enums import Relationships
from ..announcement import Announcement as Ann
from .bgp_policy import BGPPolicy


class BGPRIBSPolicy(BGPPolicy):
    __slots__ = ["ribs_in", "ribs_out", "recv_q", "send_q"]

    def __init__(self, *args, **kwargs):
        super(BGPRIBSPolicy, self).__init__(*args, **kwargs)
        self.ribs_in = RibsIn()
        self.ribs_out = RibsOut()
        self.recv_q = RecvQueue()
        self.send_q = SendQueue()

    def _propagate(policy_self, self, propagate_to: Relationships, send_rels: list):
        """Propogates announcements to other ASes

        send_rels is the relationships that are acceptable to send
        """

        for as_obj in getattr(self, propagate_to.name.lower()):
            for prefix, ann in policy_self.local_rib.items():
                if ann.recv_relationship in send_rels:
                    # Update RIBs out
                        if ann not in policy_self.ribs_out[as_obj.asn][prefix]:
                            policy_self.ribs_out[as_obj.asn][prefix].append(ann)
                            policy_self.send_q[as_obj.asn][prefix].append(ann)

            # Send everything in the send queues
            for prefix, anns in policy_self.send_q[as_obj.asn].items():
                for ann in anns:
                    as_obj.policy.recv_q[self.asn][prefix].append(ann)

    def process_incoming_anns(policy_self, self, recv_relationship: Relationships,
        recv_q=None, limit_prefix=None):
        """Process all announcements that were incoming from a specific rel"""

        if recv_q is None:
            recv_q = policy_self.recv_q

        for neighbor, value in recv_q.items():
            for prefix, ann_list in value.items():
                if limit_prefix is not None and limit_prefix != prefix:
                    # limit_prefix allows limiting processing to a specific prefix
                    continue
                # Get announcement currently in local rib
                og_best_ann = policy_self.local_rib.get(prefix)
                best_ann = og_best_ann
                # Done here to optimize
                if best_ann is not None and best_ann.seed_asn is not None:
                    continue

                # Another optimization, there is never a possibility of an
                # announcement from a worse relationship replacing one from a
                # better one, so don't bother checking
                possible_replace = (True if best_ann is None else 
                    best_ann.recv_relationship.value <= recv_relationship.value)

                # For each announcement that is incoming
                for ann in ann_list:
                    if ann.withdraw:
                        # Remove withdrawn routes
                        ann_to_remove = deepcopy(ann)
                        ann_to_remove.withdraw = False
                        policy_self.ribs_in[neighbor][prefix].remove(ann_to_remove)
                        # Update AS path for loc_rib and ribs_out
                        ann_to_remove.as_path = (self.asn, *ann.as_path)
                        self.loc_rib[prefix].remove(ann_to_remove)
                        policy_self.withdraw_route(self, ann_to_remove)
                        # Get next-best announcement from ribs_in
                        self.loc_rib[prefix] = policy_self.process_incoming_anns(self, recv_relationship, 
                            recv_q=policy_self.ribs_in, limit_prefix=prefix)
                        continue

                    if not ann in policy_self.ribs_in[neighbor][prefix]:
                        # If never seen before, copy to ribs_in
                        policy_self.ribs_in[neighbor][prefix].append(ann)

                    new_ann_is_better = (True if best_ann is None else 
                        policy_self._new_ann_is_better(self, best_ann, ann, recv_relationship))
                    # If the new priority is higher
                    if new_ann_is_better:
                        best_ann = deepcopy(ann)
                        best_ann.seed_asn = None
                        best_ann.as_path = (self.asn, *ann.as_path)
                        best_ann.recv_relationship = recv_relationship
                        # Save to local rib
                        policy_self.local_rib[prefix] = best_ann
                        # Update RIBs out, remove old announcement only
                        if og_best_ann is not None:
                            policy_self.withdraw_route(self, og_best_ann)

        if recv_q == policy_self.recv_q and limit_prefix is None:
            # If this is the normal processing of announcements, reset the recv_q
            policy_self.recv_q = RecvQueue()

    def withdraw_route(policy_self, self, ann_to_remove):
        """Withdraw a route from all neighbors. 

        This function will not remove an announcement from the local rib, that
        should be done before calling this function.
        """
        prefix = ann_to_remove.prefix
        for send_neighbor in policy_self.ribs_out:
            if ann_to_remove in policy_self.ribs_out[send_neighbor][prefix]:
                if ann_to_remove in policy_self.send_q[send_neighbor][prefix]:
                    # If the withdrawn route has not been sent to the send_neighbor yet, don't send it
                    policy_self.send_q[send_neighbor][prefix].remove(ann_to_remove)
                else:
                    # Otherwise propagate the withdrawal
                    withdraw = deepcopy(ann_to_remove)
                    withdraw.withdraw = True
                    policy_self.send_q[send_neighbor][prefix].append(withdraw)
                policy_self.ribs_out[send_neighbor][prefix].remove(ann_to_remove)


    def _new_ann_is_better(policy_self, self, deep_ann, shallow_ann, recv_relationship: Relationships):
        """Assigns the priority to an announcement according to Gao Rexford"""

        if deep_ann.recv_relationship.value > recv_relationship.value:
            return False
        elif deep_ann.recv_relationship.value < recv_relationship.value:
            return True
        else:
            if len(deep_ann.as_path) < len(shallow_ann.as_path) + 1:
                return False
            elif len(deep_ann.as_path) > len(shallow_ann.as_path) + 1:
                return True
            else:
                if deep_ann.as_path[0] <= self.asn:
                    return False
                else:
                    return True
