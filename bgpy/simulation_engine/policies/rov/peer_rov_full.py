from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull

from .peer_rov import PeerROV


class PeerROVFull(PeerROV, BGPFull):
    """An Policy that deploys ROV only for peers"""

    name: str = "PeerROV Full"
