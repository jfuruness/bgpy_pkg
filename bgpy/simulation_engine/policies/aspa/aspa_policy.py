from .aspa_simple_policy import ASPASimplePolicy

from bgpy.simulation_engine.policies.bgp.bgp_policy import BGPPolicy


class ASPAPolicy(ASPASimplePolicy, BGPPolicy):
    """An Policy that deploys ASPA and has withdrawals, ribs in and out"""

    name: str = "ASPA"
