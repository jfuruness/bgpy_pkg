from bgpy.simulation_engine.policies.bgp import BGPPolicy

from .peer_rov_simple_policy import PeerROVSimplePolicy


class PeerROVPolicy(PeerROVSimplePolicy, BGPPolicy):
    """An Policy that deploys ROV only for peers"""

    name: str = "PeerROV"
