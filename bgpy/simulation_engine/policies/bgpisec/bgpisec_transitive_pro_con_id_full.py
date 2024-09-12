from bgpy.simulation_engine.policies.rov.rov_full import ROVFull

from .bgpisec import BGPiSec


class BGPiSecFull(BGPiSec, ROVFull):
    """BGP-iSec with withdrawals, ribs in and out"""

    name = "BGP-iSec Full"
