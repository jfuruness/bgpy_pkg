from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .bgpisec_transitive import BGPiSecTransitive


class BGPiSecTransitiveFull(BGPiSecTransitive, ROVFull):
    """BGP-iSecTransitive with withdrawals, ribs in and out"""

    name = "BGP-iSec Transitive Full"
