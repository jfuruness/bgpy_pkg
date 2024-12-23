from .bgp_full_ignore_invalid import BGPFullIgnoreInvalid


class BGPFullSuppressWithdrawals(BGPFullIgnoreInvalid):
    """Drops all withdrawals"""

    name = "BGP Full Suppress Withdrawals"

    def _policy_propagate(
        self: "BGP",
        neighbor: "AS",
        ann: "Ann",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> bool:
        """Custom policy propagation that can be overriden

        In this case, fails to forward withdrawals
        """

        # Returns True if withdraw, indicating that this function
        # handled propagation (and did not forward the withdrawal)
        # if withdraw is False, propagation continues as normal
        return ann.withdraw
