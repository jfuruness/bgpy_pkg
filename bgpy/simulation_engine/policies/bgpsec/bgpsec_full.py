from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull

from .bgpsec import BGPSec


class BGPSecFull(BGPSec, BGPFull):
    """Represents BGPSec with withdrawals, ribsin, ribs out"""

    name: str = "BGPsec Full"
