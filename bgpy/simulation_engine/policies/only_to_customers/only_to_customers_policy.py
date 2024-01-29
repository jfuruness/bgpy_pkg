from .only_to_customers_simple_policy import OnlyToCustomersSimplePolicy

from bgpy.simulation_engine.policies.bgp.bgp_policy import BGPPolicy


class OnlyToCustomersPolicy(OnlyToCustomersSimplePolicy, BGPPolicy):
    """An Policy that deploys OnlyToCustomers and has withdrawals, ribs in and out"""

    name: str = "OnlyToCustomers"
