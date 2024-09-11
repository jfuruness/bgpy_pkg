from typing import TYPE_CHECKING

from .aspa import ASPA

if TYPE_CHECKING:
    from bgpy.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann


class ASPAwN(ASPA):
    """Esentially ASPA and checking neighbors at every AS together"""

    name = "ASPAwN"

    def _valid_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:  # type: ignore
        """Combines ASPA valid and checking neighbors at every AS"""

        as_path = ann.as_path
        as_dict = self.as_.as_graph.as_dict
        for i, asn in enumerate(as_path):
            # Get the AS object for the current AS in the AS Path
            aspawn_as_obj = as_dict[asn]
            # If the AS is an ASPAwN AS
            if isinstance(aspawn_as_obj.policy, ASPAwN):
                # Check that both of it's neighbors are in the valid next hops
                for neighbor_index in (i - 1, i + 1):
                    # Can't use try except IndexError here, since -1 is a valid index
                    if 0 <= neighbor_index < len(as_path):
                        neighbor_asn = as_path[neighbor_index]
                        if neighbor_asn not in aspawn_as_obj.neighbor_asns:
                            return False
        rv = super()._valid_ann(ann, from_rel)
        assert isinstance(rv, bool), "mypy"
        return rv
