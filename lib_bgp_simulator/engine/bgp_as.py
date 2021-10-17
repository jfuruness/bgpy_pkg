from lib_caida_collector import AS

from .ann_containers import LocalRib
from .ann_containers import RecvQueue
from ..enums import Relationships
from ..announcement import Announcement as Ann


class BGPAS(AS):
    # TODO: fix later? class error? Does this impact speed?
    __slots__ = ("_local_rib", "_recv_q", "_ribs_in", "_ribs_out", "_send_q")

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
               "Please make a class attr name for the policy something else")
        assert len(set(cls.subclass_names)) == len(cls.subclass_names), msg

    def __init__(self, *args, **kwargs):
        """Add local rib and data structures here

        This way they can be easily cleared later without having to redo
        the graph
        """

        if kwargs.get("reset_base", True):
            super(BGPAS, self).__init__(*args, **kwargs)
        self._local_rib = LocalRib()
        self._recv_q = RecvQueue()

    def propagate_to_providers(self):
        """Propogates to providers"""

        send_rels = set([Relationships.ORIGIN, Relationships.CUSTOMERS])
        self._propagate(Relationships.PROVIDERS, send_rels)

    def propagate_to_customers(self):
        """Propogates to customers"""

        send_rels = set([Relationships.ORIGIN,
                         Relationships.CUSTOMERS,
                         Relationships.PEERS,
                         Relationships.PROVIDERS])
        self._propagate(Relationships.CUSTOMERS, send_rels)

    def propagate_to_peers(self):
        """Propogates to peers"""

        send_rels = set([Relationships.ORIGIN,
                         Relationships.CUSTOMERS])
        self._propagate(Relationships.PEERS, send_rels)

    def _propagate(self, propagate_to: Relationships, send_rels: list):
        """Propogates announcements from local rib to other ASes

        send_rels is the relationships that are acceptable to send

        Later you can change this so it's not the local rib that's
        being sent. But this is just proof of concept.
        """

        for neighbor in getattr(self, propagate_to.name.lower()):
            for prefix, ann in self._local_rib.prefix_anns():
                if ann.recv_relationship in send_rels:
                    propagate_args = [neighbor, ann, propagate_to, send_rels]
                    # Policy took care of it's own propagation for this ann
                    if self._policy_propagate(*propagate_args):
                        continue
                    else:
                        self._process_outgoing_ann(*propagate_args)

    def _policy_propagate(*args, **kwargs):
        """Custom policy propagation that can be overriden"""

        return False

    def _process_outgoing_ann(self, neighbor, ann, propagate_to, send_rels):
        """Adds ann to the neighbors recv q"""

        # Add the new ann to the incoming anns for that prefix
        neighbor.receive_ann(ann)

    def receive_ann(self, ann: Ann):
        self._recv_q.add_ann(ann)

    def process_incoming_anns(self,
                              from_rel: Relationships,
                              *args,
                              propagation_round=None,
                              attack=None,  # Usually None
                              reset_q=True,
                              **kwargs):
        """Process all announcements that were incoming from a specific rel"""

        for prefix, ann_list in self._recv_q.prefix_anns():
            # Get announcement currently in local rib
            current_ann = self._local_rib.get_ann(prefix)
            current_processed = True

            # Seeded Ann will never be overriden, so continue
            if getattr(current_ann, "seed_asn", None) is not None:
                continue

            # For each announcement that was incoming
            for ann in ann_list:
                # Make sure there are no loops
                # In ROV subclass also check roa validity
                if self._valid_ann(ann, from_rel):
                    new_ann_better = self._new_ann_better(current_ann,
                                                          current_processed,
                                                          from_rel,
                                                          ann,
                                                          False,
                                                          from_rel)
                    if new_ann_better:
                        current_ann = ann
                        current_processed = False

            # This is a new best ann. Process it and add it to the local rib
            if current_processed is False:
                current_ann = self._copy_and_process(current_ann, from_rel)
                # Save to local rib
                self._local_rib.add_ann(current_ann)

        self._reset_q(reset_q)

    def _valid_ann(self, ann, recv_relationship):
        """Determine if an announcement is valid or should be dropped"""

        # BGP Loop Prevention Check
        return not (self.asn in ann.as_path)

    def _copy_and_process(self, ann, recv_relationship, **extra_kwargs):
        """Deep copies ann and modifies attrs"""

        kwargs = {"as_path": (self.asn,) + ann.as_path,
                  "recv_relationship": recv_relationship}
        kwargs.update(extra_kwargs)

        return ann.copy(**kwargs)

    def _reset_q(self, reset_q):
        if reset_q:
            self._recv_q = RecvQueue()

    from .gao_rexford import _new_ann_better
    from .gao_rexford import _new_as_path_ties_better
    from .gao_rexford import _new_rel_better
    from .gao_rexford import _new_as_path_shorter
    from .gao_rexford import _new_wins_ties
