from typing import TYPE_CHECKING

from bgpy.simulation_engine.policies.policy import Policy

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann

    from .bgp_full import BGPFull


def _propagate(
    self: "BGPFull",
    propagate_to: "Relationships",
    send_rels: set["Relationships"],
):
    """Propogates announcements to other ASes

    send_rels is the relationships that are acceptable to send
    """
    # _policy_propagate and _add_ann_to_q have been overriden
    # So that instead of propagating, announcements end up in the send_q
    # Send q contains both announcements and withdrawals
    self._populate_send_q(propagate_to, send_rels)
    # Send announcements/withdrawals and add to ribs out
    self._send_anns(propagate_to)


def _prev_sent(self: "BGPFull", neighbor: "AS", ann: "Ann") -> bool:
    """Don't send what we've already sent"""
    ribs_out_ann: Ann | None = self.ribs_out.get_ann(neighbor.asn, ann.prefix)
    return ann.prefix_path_attributes_eq(ribs_out_ann)


def _process_outgoing_ann(
    self: "BGPFull",
    neighbor: Policy,
    ann: "Ann",
    propagate_to,
    send_rels: set["Relationships"],
):
    self.send_q.add_ann(neighbor.asn, ann)


def _send_anns(self: "BGPFull", propagate_to: "Relationships"):
    """Sends announcements and populates ribs out"""

    neighbors: list[AS] = getattr(self.as_, propagate_to.name.lower())

    for neighbor, _prefix, ann in self.send_q.info(neighbors):
        neighbor.policy.receive_ann(ann)
        # Update Ribs out if it's not a withdraw
        if not ann.withdraw:
            self.ribs_out.add_ann(neighbor.asn, ann)
    for neighbor in neighbors:
        # Resets neighbor, removing all their SendInfo
        self.send_q.pop(neighbor.asn, None)
