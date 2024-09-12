from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships
from bgpy.simulation_engine.policies.only_to_customers import OnlyToCustomers

from .bgpisec_transitive import BGPiSecTransitive

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine.announcement import Announcement as Ann


class BGPiSecTransitiveOnlyToCustomers(BGPiSecTransitive):
    """Represents BGPiSec Transitive attributes"""

    name = "BGP-iSec Transitive + OTC"

    def _valid_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:
        """Determines bgp-isec transitive+OTC validity and super() validity"""

        # Suppress this, using mixins instead of weird OO inheritance
        otc_valid = OnlyToCustomers._only_to_customers_valid(  # noqa: SLF001
            self, ann, from_rel
        )
        return otc_valid and super()._valid_ann(ann, from_rel)

    def _policy_propagate(
        self,
        neighbor: "AS",
        ann: "Ann",
        propagate_to: "Relationships",
        send_rels: set["Relationships"],
    ) -> bool:
        """If propagating to customers and only_to_customers isn't set, set it"""

        overwrite_default_kwargs = {
            "bgpsec_next_asn": neighbor.asn,
            "bgpsec_as_path": ann.bgpsec_as_path,
        }

        if propagate_to.value in (
            Relationships.CUSTOMERS.value,
            Relationships.PEERS.value,
        ):
            # NOTE: bgpisec protects this attribute
            overwrite_default_kwargs["only_to_customers"] = self.as_.asn

        send_ann = ann.copy(overwrite_default_kwargs)
        self._process_outgoing_ann(neighbor, send_ann, propagate_to, send_rels)
        return True
