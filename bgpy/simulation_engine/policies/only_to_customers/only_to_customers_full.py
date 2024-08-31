from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull

from .only_to_customers import OnlyToCustomers


class OnlyToCustomersFull(OnlyToCustomers, BGPFull):
    """An Policy that deploys OnlyToCustomers and has withdrawals, ribs in and out"""

    name: str = "OnlyToCustomers Full"
