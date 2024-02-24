from .rov import ROV

from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull


class ROVFull(ROV, BGPFull):
    """An Policy that deploys ROV and has withdrawals, ribs in and out"""

    name: str = "ROV Full"
