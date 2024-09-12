from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .bgpisec_transitive_only_to_customers import BGPiSecTransitiveOnlyToCustomers


class BGPiSecTransitiveOnlyToCustomersFull(BGPiSecTransitiveOnlyToCustomers, ROVFull):
    """BGP-iSecTransitiveOTC with withdrawals, ribs in and out"""

    name = "BGP-iSec Transitive + OTC Full"
