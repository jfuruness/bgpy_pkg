from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships
from bgpy.simulation_engine.policies.rov import ROV

if TYPE_CHECKING:
    from bgpy.simulation_engine.announcement import Announcement as Ann


class ProviderConeID(ROV):
    """Represents Provider cone ID

    Checks that all adopting ASNs in the AS Path are in the origin's provider cone

    Subclassed from ROV since nobody would bother using this if ROV wasn't deployed
    """

    name = "ProviderConeID"

    def _valid_ann(
        self,
        ann: "Ann",
        from_rel: "Relationships",
    ) -> bool:
        """Determines bgp-isec transitive validity and super() validity"""

        provider_cone_valid = self._provider_cone_valid(ann, from_rel)
        return provider_cone_valid and super()._valid_ann(ann, from_rel)

    def _provider_cone_valid(
        self,
        ann: "Ann",
        from_rel: "Relationships",
    ) -> bool:
        """Determines provider cone validity from customers"""

        if from_rel == Relationships.CUSTOMERS:
            as_dict = self.as_.as_graph.as_dict
            provider_cone_asns = as_dict[ann.origin].provider_cone_asns
            Cls = self.__class__
            if provider_cone_asns is None:
                raise ValueError(
                    "Provider cones must be set for this policy to work, see params "
                    "to simulation.py in the simulation_framework of bgpy"
                )
            # We don't look at the last ASN in the path, since that's the origin
            # The ASes ASN is also not yet in the announcement, so we add it here
            for asn in (self.as_.asn, *ann.as_path[:-1]):
                # not in provider cone of the origin, and is adopting
                if asn not in provider_cone_asns and isinstance(
                    as_dict[asn].policy, Cls
                ):
                    return False

            return True
        else:
            return True
