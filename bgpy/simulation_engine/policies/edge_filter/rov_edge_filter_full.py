from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull

from .rov_edge_filter import ROVEdgeFilter


class ROVEdgeFilterFull(ROVEdgeFilter, BGPFull):
    """Represents ROVEdgeFilter with withdrawals, ribsin, ribs out"""

    name: str = "ROV + EdgeFilter Full"
