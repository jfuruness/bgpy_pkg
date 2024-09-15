from bgpy.simulation_engine.policies.bgp.bgp_full import BGPFull

from .edge_filter import EdgeFilter


class EdgeFilterFull(EdgeFilter, BGPFull):
    """Represents EdgeFilter with withdrawals, ribsin, ribs out"""

    name: str = "EdgeFilter Full"
