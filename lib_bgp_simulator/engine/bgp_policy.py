from copy import deepcopy
import functools

from lib_caida_collector import AS

from .ann_containers import LocalRib
from .ann_containers import RecvQueue
from ..enums import Relationships
from ..announcement import Announcement as Ann


class BGPPolicy:
    __slots__ = ["local_rib", "recv_q"]

    name = "BGP"
    subclass_names = []

    def __init_subclass__(cls, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to know all attackers that have been created
        """

        super().__init_subclass__(**kwargs)
        assert hasattr(cls, "name"), "Policy must have a name"
        cls.subclass_names.append(cls.name)
        msg = (f"Duplicate name {cls.name} with {cls.__name__}."
               "Please make a class attr name for the policy something different")
        assert len(set(cls.subclass_names)) == len(cls.subclass_names), msg

    def __init__(self):
        """Add local rib and data structures here

        This way they can be easily cleared later without having to redo
        the graph
        """

        self.local_rib = LocalRib()
        self.recv_q = RecvQueue()

    def propagate_to_providers(policy_self, self):
        """Propogates to providers"""

        send_rels = set([Relationships.ORIGIN, Relationships.CUSTOMERS])
        policy_self._propagate(self, Relationships.PROVIDERS, send_rels)

    def propagate_to_customers(policy_self, self):
        """Propogates to customers"""

        send_rels = set([Relationships.ORIGIN,
                         Relationships.CUSTOMERS,
                         Relationships.PEERS,
                         Relationships.PROVIDERS])
        policy_self._propagate(self, Relationships.CUSTOMERS, send_rels)

    def propagate_to_peers(policy_self, self):
        """Propogates to peers"""

        send_rels = set([Relationships.ORIGIN,
                         Relationships.CUSTOMERS])
        policy_self._propagate(self, Relationships.PEERS, send_rels)

    def _propagate(policy_self, self, propagate_to: Relationships, send_rels: list):
        """Propogates announcements from local rib to other ASes

        send_rels is the relationships that are acceptable to send

        Later you can change this so it's not the local rib that's
        being sent. But this is just proof of concept.
        """

        for as_obj in getattr(self, propagate_to.name.lower()):
            for prefix, ann in policy_self.local_rib.prefix_anns():#items():
                if ann.recv_relationship in send_rels:
                    # Policy took care of it's own propagation for this ann
                    if policy_self._policy_propagate(self, propagate_to, send_rels, ann, as_obj):
                        continue
                    else:
                        policy_self._add_ann_to_q(self, as_obj, ann, propagate_to, send_rels)

    def _add_ann_to_q(policy_self, self, as_obj, ann, propagate_to, send_rels):
        """Adds ann to the neighbors recv q"""

        # Add the new ann to the incoming anns for that prefix
        as_obj.policy.recv_q.add_ann(ann)

    def _policy_propagate(*args, **kwargs):
        """Custom policy propagation that can be overriden"""

        return False

    def process_incoming_anns(policy_self,
                              self,
                              recv_relationship: Relationships,
                              *args,
                              propagation_round=None,
                              attack=None,  # Usually None
                              reset_q=True,
                              **kwargs):
        """Process all announcements that were incoming from a specific rel"""

        for prefix, ann_list in policy_self.recv_q.prefix_anns():
            # Get announcement currently in local rib
            current_best_ann = policy_self.local_rib.get_ann(prefix)#get(prefix)
            current_best_ann_processed = True

            # Announcement will never be overriden, so continue
            if current_best_ann is not None and current_best_ann.seed_asn is not None:
                continue

            # For each announcement that was incoming
            for ann in ann_list:
                # Make sure there are no loops
                # In ROV subclass also check roa validity
                if policy_self._valid_ann(self, ann, recv_relationship):
                    new_ann_is_better = policy_self._new_ann_is_better(self,
                                                                       current_best_ann,
                                                                       current_best_ann_processed,
                                                                       recv_relationship,
                                                                       ann,
                                                                       False,
                                                                       recv_relationship)
                    if new_ann_is_better:
                        current_best_ann = ann
                        current_best_ann_processed = False

            # This is a new best ann. Process it and add it to the local rib
            if current_best_ann_processed is False:
                current_best_ann = policy_self._deep_copy_ann(self, current_best_ann, recv_relationship)
                # Save to local rib
                policy_self.local_rib.add_ann(current_best_ann, prefix=prefix)

        policy_self._reset_q(reset_q)

    def _reset_q(policy_self, reset_q):
        if reset_q:
            policy_self.recv_q = RecvQueue()

    def _new_ann_is_better(policy_self,
                           self,
                           current_best_ann,
                           current_best_ann_processed,
                           default_current_best_ann_recv_rel,
                           new_ann,
                           new_ann_processed,
                           default_new_ann_recv_rel):
        """Assigns the priority to an announcement according to Gao Rexford

        NOTE: processed is processed for second ann"""

        # Can't assert this here due to passing new_ann as None now that it can be prpcessed or not
        #assert self.asn not in new_ann.as_path, "Should have been removed in ann validation func"

        none_validation = policy_self._none_validation(current_best_ann, new_ann)
        if none_validation is not None:
            return none_validation
        else:
            new_ann_is_better_no_tiebreaks = policy_self._new_ann_is_better_no_tiebreaks(len(current_best_ann.as_path),
                                                                                         current_best_ann_processed,
                                                                                         current_best_ann.recv_relationship,
                                                                                         default_current_best_ann_recv_rel,
                                                                                         len(new_ann.as_path),
                                                                                         new_ann_processed,
                                                                                         new_ann.recv_relationship,
                                                                                         default_new_ann_recv_rel)
            if new_ann_is_better_no_tiebreaks is not None:
                return new_ann_is_better_no_tiebreaks
            else:
                return policy_self._new_ann_wins_ties(current_best_ann, current_best_ann_processed, new_ann, new_ann_processed)

    def _none_validation(policy_self, current_best_ann, new_ann):
        if current_best_ann is None:
            return True
        elif new_ann is None:
            return False
        else:
            return None

    def _new_ann_is_better_no_tiebreaks(policy_self,
                                        current_best_as_path_len,
                                        current_best_processed,
                                        current_best_recv_relationship,
                                        default_current_best_ann_recv_rel,
                                        new_ann_as_path_len,
                                        new_ann_processed,
                                        new_ann_recv_relationship,
                                        default_new_ann_recv_rel):
        new_rel_is_better = policy_self._new_relationship_is_better(current_best_recv_relationship,
                                                                    current_best_processed,
                                                                    default_current_best_ann_recv_rel,
                                                                    new_ann_recv_relationship,
                                                                    new_ann_processed,
                                                                    default_new_ann_recv_rel)
        if new_rel_is_better is not None:
            return new_rel_is_better
        else:
            return policy_self._new_as_path_is_shorter(current_best_as_path_len,
                                                       current_best_processed,
                                                       new_ann_as_path_len,
                                                       new_ann_processed)

    def _new_relationship_is_better(policy_self,
                                    current_best_ann_recv_relationship,
                                    current_best_processed,
                                    default_current_best_ann_recv_rel,
                                    new_ann_recv_relationship,
                                    new_ann_processed,
                                    default_new_ann_recv_rel
                                    ):


        current_best_rel = current_best_ann_recv_relationship if current_best_processed else default_current_best_ann_recv_rel
        new_rel = new_ann_recv_relationship if new_ann_processed else default_new_ann_recv_rel

        if current_best_rel.value > new_rel.value:
            return False
        elif current_best_rel.value < new_rel.value:
            return True
        else:
            return None


    def _new_as_path_is_shorter(policy_self, current_best_as_path_len, current_best_ann_processed, new_as_path_len, new_ann_processed):
        if current_best_as_path_len + int(not current_best_ann_processed) < new_as_path_len + int(not new_ann_processed):
            return False
        elif current_best_as_path_len + int(not current_best_ann_processed) > new_as_path_len + int(not new_ann_processed):
            return True
        else:
            return None

    def _new_ann_wins_ties(policy_self, current_best_ann, current_best_ann_processed, new_ann, new_ann_processed) -> bool:
        current_best_index = min(int(current_best_ann_processed), len(current_best_ann.as_path) - 1)
        new_index = min(int(new_ann_processed), len(new_ann.as_path) - 1)
        assert current_best_ann.as_path[current_best_index] != new_ann.as_path[new_index], "Cameron says no ties lol"

        return new_ann.as_path[new_index] < current_best_ann.as_path[current_best_index]

    def _deep_copy_ann(policy_self, self, ann, recv_relationship, **extra_kwargs):
        """Deep copies ann and modifies attrs"""

        kwargs = {"as_path": (self.asn, *ann.as_path)}
        kwargs.update(extra_kwargs)

        return ann.copy(recv_relationship=recv_relationship, **kwargs)

    def _valid_ann(policy_self, self, ann, recv_relationship):
        """Determine if an announcement is valid or should be dropped"""

        # BGP Loop Prevention Check
        return not (self.asn in ann.as_path)
