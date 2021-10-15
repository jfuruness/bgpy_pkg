from lib_caida_collector import AS

from ...ann_containers import LocalRib
from ...ann_containers import RecvQueue
from ....enums import Relationships
from ....announcements import Announcement as Ann


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
