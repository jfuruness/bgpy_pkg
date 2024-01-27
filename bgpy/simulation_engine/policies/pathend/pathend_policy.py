from .pathend_simple_policy import PathendSimplePolicy

from bgpy.simulation_engine.policies.bgp.bgp_policy import BGPPolicy


class PathendPolicy(PathendSimplePolicy, BGPPolicy):
    """An Policy that deploys Pathend and has withdrawals, ribs in and out"""

    name: str = "Pathend"
