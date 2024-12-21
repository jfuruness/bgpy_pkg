from typing import TYPE_CHECKING

from bgpy.simulation_engine.policies.policy import Policy

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann

    from .bgp_full import BGPFull


def _prev_sent(self: "BGPFull", neighbor: "AS", ann: "Ann") -> bool:
    """Don't send what we've already sent"""
    return ann == self.ribs_out.get_ann(neighbor.asn, ann.prefix)


def _process_outgoing_ann(
    self: "BGPFull",
    neighbor: Policy,
    ann: "Ann",
    propagate_to,
    send_rels: set["Relationships"],
):
    if not ann.withdraw:
        self.ribs_out.add_ann(neighbor.asn, ann)
    super()._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)
