from typing import TYPE_CHECKING

from .bgpisec_transitive_only_to_customers import BGPiSecTransitiveOnlyToCustomers
from .provider_cone_id import ProviderConeID

if TYPE_CHECKING:
    from bgpy.enums import Relationships
    from bgpy.simulation_engine.announcement import Announcement as Ann


class BGPiSec(BGPiSecTransitiveOnlyToCustomers):
    """Represents BGPiSec (Transitive attributes, ProConeID, protected OTC)

    NOTE: OTC isn't "protected" in a code sense, but don't let your attacks
    remove this. Not sure how it would be protected in a code sense honestly
    without significantly modifying and slowing down the announcement copying
    """

    name = "BGP-iSec"

    def _valid_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """Determines bgp-isec transitive + OTC + ProviderConeValid + super"""

        # Ignore private member access, just using mixins instead of weird OO
        pro_cone_id_valid = ProviderConeID._provider_cone_valid(  # noqa: SLF001
            self, ann, from_rel
        )
        return pro_cone_id_valid and super()._valid_ann(ann, from_rel)
