from .aspa import ASPA

from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull


class ASPAFull(ASPA, BGPFull):
    """An Policy that deploys ASPA and has withdrawals, ribs in and out"""

    name: str = "ASPA Full"
