from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull

from .peerlock_lite import PeerlockLite


class PeerlockLiteFull(PeerlockLite, BGPFull):
    """An Policy that deploys PeerlockLite and has withdrawals, ribs in and out"""

    name: str = "PeerlockLite Full"
