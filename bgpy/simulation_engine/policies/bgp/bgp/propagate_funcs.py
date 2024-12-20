from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine.announcements import Announcement as Ann

    from .bgp import BGP


def propagate_to_providers(self) -> None:
    """Propogates to providers

    Propogate ann's that have a recv_rel of origin or customer to providers
    """

    send_rels: set[Relationships] = {
        Relationships.ORIGIN,
        Relationships.CUSTOMERS,
    }
    self._propagate(self.as_.providers, Relationships.PROVIDERS, send_rels)


def propagate_to_customers(self) -> None:
    """Propogates to customers"""

    # Anns that have any of these as recv_rel get propogated
    send_rels: set[Relationships] = {
        Relationships.ORIGIN,
        Relationships.CUSTOMERS,
        Relationships.PEERS,
        Relationships.PROVIDERS,
    }
    self._propagate(self.as_.customers, Relationships.CUSTOMERS, send_rels)


def propagate_to_peers(self) -> None:
    """Propogates to peers"""

    # Anns that have any of these as recv_rel get propogated
    send_rels: set[Relationships] = {
        Relationships.ORIGIN,
        Relationships.CUSTOMERS,
    }
    self._propagate(self.as_.peers, Relationships.PEERS, send_rels)


def _propagate(
    self: "BGP",
    relevant_neighbors,
    propagate_to: Relationships,
    send_rels: set[Relationships],
) -> None:
    """Propogates announcements from local rib to other ASes

    send_rels is the relationships that are acceptable to send
    """

    for _prefix, unprocessed_ann in self.local_rib.items():
        if unprocessed_ann.recv_relationship in send_rels:
            # NOTE: Commenting this out made zero difference. Literally none
            # ann = unprocessed_ann.__class__(
            #     prefix=unprocessed_ann.prefix,
            #     as_path=unprocessed_ann.as_path,
            #     next_hop_asn=self.as_.asn,
            #     seed_asn=None,
            #     recv_relationship=unprocessed_ann.recv_relationship,
           #  )

            for neighbor in relevant_neighbors:
                neighbor.policy.recv_q.add_ann(unprocessed_ann)


def _policy_propagate(
    self: "BGP",
    neighbor: "AS",
    ann: "Ann",
    propagate_to: Relationships,
    send_rels: set[Relationships],
) -> bool:
    """Custom policy propagation that can be overriden"""

    return False


def _prev_sent(self: "BGP", neighbor: "AS", ann: "Ann") -> bool:
    """Don't resend anything for BGPAS. For this class it doesn't matter"""
    return False


def _process_outgoing_ann(
    self: "BGP",
    neighbor: "AS",
    ann: "Ann",
    propagate_to: Relationships,
    send_rels: set[Relationships],
) -> None:
    """Adds ann to the neighbors recv q"""

    # Add the new ann to the incoming anns for that prefix
    neighbor.policy.receive_ann(ann)
