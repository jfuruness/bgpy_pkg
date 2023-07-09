from bgpy.caida_collector import AS

from bgpy.simulation_engine.announcement import Announcement as Ann
from bgpy.enums import Relationships


def propagate_to_providers(self):
    """Propogates to providers

    Propogate ann's that have a recv_rel of origin or customer to providers
    """

    send_rels: set[Relationships] = set([Relationships.ORIGIN, Relationships.CUSTOMERS])
    self._propagate(Relationships.PROVIDERS, send_rels)


def propagate_to_customers(self):
    """Propogates to customers"""

    # Anns that have any of these as recv_rel get propogated
    send_rels: set[Relationships] = set(
        [
            Relationships.ORIGIN,
            Relationships.CUSTOMERS,
            Relationships.PEERS,
            Relationships.PROVIDERS,
        ]
    )
    self._propagate(Relationships.CUSTOMERS, send_rels)


def propagate_to_peers(self):
    """Propogates to peers"""

    # Anns that have any of these as recv_rel get propogated
    send_rels: set[Relationships] = set([Relationships.ORIGIN, Relationships.CUSTOMERS])
    self._propagate(Relationships.PEERS, send_rels)


def _propagate(self, propagate_to: Relationships, send_rels: list[Relationships]):
    """Propogates announcements from local rib to other ASes

    send_rels is the relationships that are acceptable to send
    """

    for neighbor in getattr(self, propagate_to.name.lower()):
        for prefix, ann in self._local_rib.prefix_anns():
            if ann.recv_relationship in send_rels and not self._prev_sent(
                neighbor, ann
            ):
                propagate_args = [neighbor, ann, propagate_to, send_rels]
                # Policy took care of it's own propagation for this ann
                if self._policy_propagate(*propagate_args):
                    continue
                else:
                    self._process_outgoing_ann(*propagate_args)


def _policy_propagate(*args, **kwargs) -> bool:
    """Custom policy propagation that can be overriden"""

    return False


def _prev_sent(*args, **kwargs) -> bool:
    """Don't resend anything for BGPAS. For this class it doesn't matter"""
    return False


def _process_outgoing_ann(
    self,
    neighbor: AS,
    ann: Ann,
    propagate_to: Relationships,
    send_rels: list[Relationships],
):
    """Adds ann to the neighbors recv q"""

    # Add the new ann to the incoming anns for that prefix
    neighbor.receive_ann(ann)
