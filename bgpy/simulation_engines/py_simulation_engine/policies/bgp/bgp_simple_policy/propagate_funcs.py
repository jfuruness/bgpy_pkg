from typing import TYPE_CHECKING, Union

from bgpy.enums import PyRelationships


if TYPE_CHECKING:
    from bgpy.as_graphs import AS

    from bgpy.simulation_engines.cpp_simulation_engine.cpp_announcement import (
        CPPAnnouncement as CPPAnn,
    )

    from bgpy.simulation_engines.py_simulation_engine.py_announcement import (
        PyAnnouncement as PyAnn,
    )
    from bgpy.enums import CPPRelationships


def propagate_to_providers(self) -> None:
    """Propogates to providers

    Propogate ann's that have a recv_rel of origin or customer to providers
    """

    send_rels: set[Union["PyRelationships", "CPPRelationships"]] = set(
        [PyRelationships.ORIGIN, PyRelationships.CUSTOMERS]
    )
    self._propagate(PyRelationships.PROVIDERS, send_rels)


def propagate_to_customers(self) -> None:
    """Propogates to customers"""

    # Anns that have any of these as recv_rel get propogated
    send_rels: set[Union["PyRelationships", "CPPRelationships"]] = set(
        [
            PyRelationships.ORIGIN,
            PyRelationships.CUSTOMERS,
            PyRelationships.PEERS,
            PyRelationships.PROVIDERS,
        ]
    )
    self._propagate(PyRelationships.CUSTOMERS, send_rels)


def propagate_to_peers(self) -> None:
    """Propogates to peers"""

    # Anns that have any of these as recv_rel get propogated
    send_rels: set[Union["PyRelationships", "CPPRelationships"]] = set(
        [PyRelationships.ORIGIN, PyRelationships.CUSTOMERS]
    )
    self._propagate(PyRelationships.PEERS, send_rels)


def _propagate(
    self,
    propagate_to: Union["PyRelationships", "CPPRelationships"],
    send_rels: set[Union["PyRelationships", "CPPRelationships"]],
) -> None:
    """Propogates announcements from local rib to other ASes

    send_rels is the relationships that are acceptable to send
    """

    if propagate_to == PyRelationships.PROVIDERS:
        neighbors = self.as_.providers
    elif propagate_to == PyRelationships.PEERS:
        neighbors = self.as_.peers
    elif propagate_to == PyRelationships.CUSTOMERS:
        neighbors = self.as_.customers
    else:
        raise NotImplementedError

    for neighbor in neighbors:
        for prefix, ann in self._local_rib.prefix_anns():
            if ann.recv_relationship in send_rels and not self._prev_sent(
                neighbor, ann
            ):
                # Policy took care of it's own propagation for this ann
                if self._policy_propagate(neighbor, ann, propagate_to, send_rels):
                    continue
                else:
                    self._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)


def _policy_propagate(
    self,
    neighbor: "AS",
    ann: Union["PyAnn", "CPPAnn"],
    propagate_to: Union["PyRelationships", "CPPRelationships"],
    send_rels: set[Union["PyRelationships", "CPPRelationships"]],
) -> bool:
    """Custom policy propagation that can be overriden"""

    return False


def _prev_sent(self, neighbor: "AS", ann: Union["PyAnn", "CPPAnn"]) -> bool:
    """Don't resend anything for BGPAS. For this class it doesn't matter"""
    return False


def _process_outgoing_ann(
    self,
    neighbor: "AS",
    ann: Union["PyAnn", "CPPAnn"],
    propagate_to: Union["PyRelationships", "CPPRelationships"],
    send_rels: set[Union["PyRelationships", "CPPRelationships"]],
):
    """Adds ann to the neighbors recv q"""

    # Add the new ann to the incoming anns for that prefix
    neighbor.policy.receive_ann(ann)
