from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .bgpisec_transitive_otc import BGPiSecTransitiveOTC


class BGPiSecTransitiveOTCFull(BGPiSecTransitiveOTC, ROVFull):
    """BGP-iSecTransitiveOTC with withdrawals, ribs in and out"""

    name = "BGP-iSec Transitive + OTC Full"
