from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull

from .path_end import PathEnd


class PathEndFull(PathEnd, BGPFull):
    """An Policy that deploys Pathend and has withdrawals, ribs in and out"""

    name: str = "Path-End Full"
