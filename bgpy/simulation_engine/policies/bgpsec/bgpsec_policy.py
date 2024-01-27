from bgpy.simulation_engine.policies.bgp.bgp_policy import BGPPolicy

from .bgpsec_simple_policy import BGPSecSimplePolicy


class BGPSecPolicy(BGPSecSimplePolicy, BGPPolicy):
    """Represents BGPSec with withdrawals, ribsin, ribs out"""

    name: str = "BGPSec"
