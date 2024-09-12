from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .bgpisec_transitive_pro_con_id import BGPiSecTransitiveProConID


class BGPiSecTransitiveProConIDFull(BGPiSecTransitiveProConID, ROVFull):
    """BGPiSecTransitiveProConID with ribs in and out and withdrawals"""

    name = "BGP-iSec Transitive + ProConID Full"
