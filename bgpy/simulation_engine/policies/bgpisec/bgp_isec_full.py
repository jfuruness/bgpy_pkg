from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull

from .bgpisec import BGPiSec


class BGPSecFull(BGPiSec, BGPFull):
    """Represents BGPiSec with withdrawals, ribsin, ribs out"""

    name: str = "BGP-iSec Full"
