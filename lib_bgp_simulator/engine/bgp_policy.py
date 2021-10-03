from copy import deepcopy

from lib_caida_collector import AS

from .local_rib import LocalRib
from .ann_queues import RecvQueue
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
        as_obj.policy.recv_q[self.asn][ann.prefix].append(ann)

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

        for neighbor, prefix_ann_dict in policy_self.recv_q.items():
            for prefix, ann_list in prefix_ann_dict.items():
                # Get announcement currently in local rib
                best_ann = policy_self.local_rib.get_ann(prefix)#get(prefix)

                # Announcement will never be overriden, so continue
                if best_ann is not None and best_ann.seed_asn is not None:
                    continue

                # For each announcement that was incoming
                for ann in ann_list:
                    # Make sure there are no loops
                    # In ROV subclass also check roa validity
                    if policy_self._valid_ann(self, ann):
                        new_ann_is_better = policy_self._new_ann_is_better(self, best_ann, ann, recv_relationship)
                        # If the new priority is higher
                        if new_ann_is_better:
                            best_ann = policy_self._deep_copy_ann(self, ann, recv_relationship)
                            # Save to local rib
                            policy_self.local_rib.add_ann(best_ann, prefix=prefix)
                            #policy_self.local_rib[prefix] = best_ann

        policy_self._reset_q(reset_q)

    def _reset_q(policy_self, reset_q):
        if reset_q:
            policy_self.recv_q = RecvQueue()

    def _new_ann_is_better(policy_self, self, deep_ann, second_ann, recv_relationship: Relationships, processed=False):
        """Assigns the priority to an announcement according to Gao Rexford

        NOTE: processed is processed for second ann"""

        assert self.asn not in second_ann.as_path, "Should have been removed in ann validation func"

        best_by_relationship = policy_self._best_by_relationship(deep_ann, second_ann if processed else recv_relationship)
        if best_by_relationship is not None:
            return best_by_relationship
        else:
            return policy_self._best_as_path_ties(self, deep_ann, second_ann, processed=processed)

    def _best_by_relationship(policy_self, deep_ann, other):
        if deep_ann is None:
            return True

        if isinstance(other, Relationships):
            other_relationship = other
        elif isinstance(other, Ann):
            other_relationship = other.recv_relationship
        else:
            raise NotImplementedError

        if deep_ann.recv_relationship.value > other_relationship.value:
            return False
        elif deep_ann.recv_relationship.value < other_relationship.value:
            return True
        else:
            return None

    def _best_as_path_ties(policy_self, self, deep_ann, second_ann, processed=False):
        best_as_path = policy_self._best_as_path(deep_ann, second_ann, processed)
        if best_as_path is not None:
            return best_as_path
        else:
            return policy_self._best_tiebreak(self, deep_ann, second_ann, processed)

    def _best_as_path(policy_self, deep_ann, second_ann, processed):
        if len(deep_ann.as_path) < len(second_ann.as_path) + int(not processed):
            return False
        elif len(deep_ann.as_path) > len(second_ann.as_path) + int(not processed):
            return True
        else:
            return None

    def _best_tiebreak(policy_self, self, deep_ann, second_ann, processed) -> bool:
        return not deep_ann.as_path[0] <= self.asn

    def _deep_copy_ann(policy_self, self, ann, recv_relationship, **extra_kwargs):
        """Deep copies ann and modifies attrs"""

        kwargs = {"as_path": (self.asn, *ann.as_path)}
        kwargs.update(extra_kwargs)

        return ann.copy(recv_relationship=recv_relationship, **kwargs)

    def _valid_ann(policy_self, self, ann):
        """Determine if an announcement is valid or should be dropped"""

        # BGP Loop Prevention Check
        return not (self.asn in ann.as_path)
