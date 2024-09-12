from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .bgpisec_transitive_pro_con_id import BGPiSecTransitiveProConID


class BGPiSecTransitiveProConIDFull(BGPiSecTransitiveProConID, ROVFull):
    """BGP-iSec with withdrawals, ribs in and out"""

    name = "BGP-iSec Transitive + ProConID Full"
