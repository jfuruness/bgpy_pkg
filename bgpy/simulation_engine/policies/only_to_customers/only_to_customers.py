from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships as Rels
from bgpy.simulation_engine.policies.bgp import BGP

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine import Announcement as Ann


class OnlyToCustomers(BGP):
    """An Policy that deploys OnlyToCustomers"""

    name: str = "OnlyToCustomers"

    def _valid_ann(self, ann: "Ann", from_rel: Rels) -> bool:
        """Returns False if from peer/customer when only_to_customers is set"""

        otc_valid = self._only_to_customers_valid(ann, from_rel)
        return otc_valid and super()._valid_ann(ann, from_rel)

    def _only_to_customers_valid(self, ann: "Ann", from_rel: Rels) -> bool:
        """Returns validity for OTC attributes"""

        if (
            (
                ann.only_to_customers
                and from_rel.value == Rels.PEERS.value
                and ann.next_hop_asn != ann.only_to_customers
            )
            or ann.only_to_customers
            and from_rel.value == Rels.CUSTOMERS.value
        ):
            return False
        else:
            return True

    def _policy_propagate(
        self,
        neighbor: "AS",
        ann: "Ann",
        propagate_to: Rels,
        send_rels: set[Rels],
    ) -> bool:
        """If propagating to customers and only_to_customers isn't set, set it"""

        if propagate_to.value in (Rels.CUSTOMERS.value, Rels.PEERS.value):
            ann = ann.copy({"only_to_customers": self.as_.asn})
            self._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)
            return True
        else:
            return False
