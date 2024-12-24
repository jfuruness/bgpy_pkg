from typing import TYPE_CHECKING

from .bgp_full_ignore_invalid import BGPFullIgnoreInvalid

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.shared.enums import Relationships
    from bgpy.simulation_engine import Announcement as Ann


class BGPFullSuppressWithdrawals(BGPFullIgnoreInvalid):
    """Drops all withdrawals"""

    name = "BGP Full Suppress Withdrawals"

    def _policy_propagate(
        self,
        neighbor: "AS",
        ann: "Ann",
        propagate_to: "Relationships",
        send_rels: set["Relationships"],
    ) -> bool:
        """Custom policy propagation that can be overriden

        In this case, fails to forward withdrawals
        """

        # Returns True if withdraw, indicating that this function
        # handled propagation (and did not forward the withdrawal)
        # if withdraw is False, propagation continues as normal
        return ann.withdraw
