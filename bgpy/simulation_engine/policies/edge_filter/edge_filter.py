from typing import TYPE_CHECKING

from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine import Announcement as Ann


class EdgeFilter(BGP):
    """Prevents edge ASes from paths containing ASNs they don't own"""

    name: str = "EdgeFilter"

    def _valid_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """Returns invalid if an edge AS is announcing paths containing other ASNs

        otherwise returns the superclasses _valid_ann (loop checking currently)
        """

        if self._valid_edge_ann(ann, from_rel):
            return super()._valid_ann(ann, from_rel)
        else:
            return False

    def _valid_edge_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """Returns invalid if an edge AS is announcing a path containing other ASNs"""

        neighbor_as_obj = self.as_.as_graph.as_dict[ann.as_path[0]]
        if (neighbor_as_obj.stub or neighbor_as_obj.multihomed) and set(
            ann.as_path
        ) != {neighbor_as_obj.asn}:
            return False
        else:
            return True
