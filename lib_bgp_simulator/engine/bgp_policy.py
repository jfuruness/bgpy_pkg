from copy import deepcopy

from lib_caida_collector import AS

from .local_rib import LocalRib
from .incoming_anns import IncomingAnns
from ..relationships import Relationships
from ..announcement import Announcement as Ann


class BGPPolicy:
    __slots__ = []

    def propagate_to_providers(policy_self, self):
        """Propogates to providers"""

        send_rels = set([Relationships.ORIGIN, Relationships.CUSTOMERS])
        policy_self._propagate(self, Relationships.PROVIDERS, send_rels)

    def propagate_to_customers(policy_self, self):
        """Propogates to customers"""

        send_rels = set([Relationships.ORIGIN,
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
            for prefix, ann in self.local_rib.items():
                if ann.recv_relationship in send_rels:
                    # Add the new ann to the incoming anns for that prefix
                    if as_obj.incoming_anns.get(prefix) is None:
                        as_obj.incoming_anns[prefix] = list()
                    as_obj.incoming_anns[prefix].append(ann)

    def process_incoming_anns(policy_self, self, recv_relationship: Relationships):
        """Process all announcements that were incoming from a specific rel"""

        for prefix, ann_list in self.incoming_anns.items():
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

            # For each announcement that was incoming
            for ann in ann_list:
                # Get the priority
                priority = policy_self._get_priority(ann, recv_relationship)
                # If the new priority is higher
                if priority > best_priority:
                    # Save the priority and announcement for later
                    # We don't copy the ann here, since we might find another better ann later
                    best_priority = priority
                    best_ann = ann

            # Now that we know the best ann, copy and save it
            # Unless it did not change
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
        self.incoming_anns = IncomingAnns()

    def _get_priority(policy_self, ann: Ann, recv_relationship: Relationships):
        """Assigns the priority to an announcement according to Gao Rexford"""

        #ann.recv_relationship = recv_relationship
        # Document this later
        # Seeded (a bool)
        # Relationship
        # Path length
        # 100 - is to invert the as_path so that longer paths are worse
        assert len(ann.as_path) < 100
        # We subtract an extra 1 because this is still the old ann
        return recv_relationship.value + 100 - len(ann.as_path) - 1
