from typing import Optional, TYPE_CHECKING

from bgpy.simulation_engine.policies.bgp.bgp_simple_policy import BGPSimplePolicy

from bgpy.simulation_engine.announcement import Announcement as Ann
from bgpy.enums import Relationships

if TYPE_CHECKING:
    from bgpy.caida_collector.graph.base_as import AS


def _propagate(self, propagate_to: Relationships, send_rels: list[Relationships]):
    """Propogates announcements to other ASes

    send_rels is the relationships that are acceptable to send
    """
    # _policy_propagate and _add_ann_to_q have been overriden
    # So that instead of propagating, announcements end up in the _send_q
    # Send q contains both announcements and withdrawals
    self._populate_send_q(propagate_to, send_rels)
    # Send announcements/withdrawals and add to ribs out
    self._send_anns(propagate_to)


def _prev_sent(self, neighbor: "AS", ann: Ann) -> bool:
    """Don't send what we've already sent"""
    ribs_out_ann: Optional[Ann] = self._ribs_out.get_ann(neighbor.asn, ann.prefix)
    return ann.prefix_path_attributes_eq(ribs_out_ann)


def _process_outgoing_ann(
    self,
    neighbor: BGPSimplePolicy,
    ann: Ann,
    propagate_to,
    send_rels: list[Relationships],
):
    self._send_q.add_ann(neighbor.asn, ann)


def _send_anns(self, propagate_to: Relationships):
    """Sends announcements and populates ribs out"""

    neighbors: list[AS] = getattr(self.as_, propagate_to.name.lower())

    for neighbor, prefix, ann in self._send_q.info(neighbors):
        neighbor.policy.receive_ann(ann)
        # Update Ribs out if it's not a withdraw
        if not ann.withdraw:
            self._ribs_out.add_ann(neighbor.asn, ann)
    for neighbor in neighbors:
        self._send_q.reset_neighbor(neighbor.asn)
