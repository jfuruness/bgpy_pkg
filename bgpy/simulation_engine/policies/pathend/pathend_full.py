from .pathend import Pathend

from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull


class PathendFull(Pathend, BGPFull):
    """An Policy that deploys Pathend and has withdrawals, ribs in and out"""

    name: str = "Pathend Full"
