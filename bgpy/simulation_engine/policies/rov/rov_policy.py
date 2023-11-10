from .rov_simple_policy import ROVSimplePolicy

from bgpy.simulation_engine.policies.bgp import BGPPolicy


class ROVPolicy(ROVSimplePolicy, BGPPolicy):
    """An Policy that deploys ROV and has withdrawals, ribs in and out"""

    name: str = "ROV"
