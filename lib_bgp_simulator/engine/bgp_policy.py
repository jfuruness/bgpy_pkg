from copy import deepcopy

from lib_caida_collector import AS

from .local_rib import LocalRib
from .incoming_anns import IncomingAnns
from .relationships import Relationships
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
            for prefix, ann in enumerate(self.local_rib):
                if ann is not None and ann.recv_relationship in send_rels:
                    # Add the new ann to the incoming anns for that prefix
                    as_obj.incoming_anns[prefix].append(ann)

    def process_incoming_anns(policy_self, self, recv_relationship: Relationships):
        """Process all announcements that were incoming from a specific rel"""

        for prefix, ann_list in enumerate(self.incoming_anns):
            # Get announcement currently in local rib
            best_ann = self.local_rib[prefix]

            # Done here to optimize
            if best_ann is not None and best_ann.seed_asn is not None:
                continue

            # For each announcement that was incoming
            for ann in ann_list:
                priority = policy_self._get_priority(ann, recv_relationship)
 
                # If the new announcement is better, save it
                # Don't bother tiebreaking, if priority is same, keep existing
                # Just like normal BGP
                # Tiebreaking with time and such should go into the priority
                # If we ever decide to do that
                if best_ann is None or best_ann.priority < priority:
                    ann = deepcopy(ann_list[0])
                    ann.seed_asn = None
                    ann.as_path = (self.asn, *ann.as_path)
                    ann.recv_relationship = recv_relationship
                    ann.priority = priority
                    best_ann = ann 
            # Save to local rib
            self.local_rib[prefix] = best_ann
        self.incoming_anns = tuple([[], [], []])

    def _get_priority(policy_self, ann: Ann, recv_relationship: Relationships):
        """Assigns the priority to an announcement according to Gao Rexford"""

        #ann.recv_relationship = recv_relationship
        # Document this later
        # Seeded (a bool)
        # Relationship
        # Path length
        # 100 - is to invert the as_path so that longer paths are worse
        assert len(ann.as_path) < 100
        return recv_relationship.value * 100 + (100 - (len(ann.as_path) + 1))
