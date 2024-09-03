from typing import TYPE_CHECKING

from bgpy.shared.enums import Relationships
from bgpy.simulation_engine.policies.rovpp.v2.base.rovpp_v2_lite import ROVPPV2Lite

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann


class ROVPPV2ImprovedLite(ROVPPV2Lite):
    """An Policy that deploys ROV++V2 Lite as defined in the ROV++ paper

    With a deviation:
    We published that an AS that recieves a hijack from it's customers
    shouldn't also send to it's customers

    Really though, this makes no sense, since you can protect your other
    customers from this by sending a competing blackhole

    When we tested this, it was slightly better than the default v2. We
    planned on publishing this in an ROV++ Journal version but scrapped
    the paper to work on other things. Have fun!

    ROV++ Improved Deployable Defense against BGP Hijacking
    """

    name: str = "ROV++V2i Lite"

    def _send_competing_hijack_allowed(
        self, ann: "Ann", propagate_to: Relationships
    ) -> bool:
        """You can send blackhole if either subprefix or non routed

        Unlike our conference paper, we don't care where the original
        hijack came from (which performs better)
        """

        return (
            # We don't care about this part (default v2), it doesn't help
            # From peer/provider
            # ann.recv_relationship
            # in [Relationships.PEERS, Relationships.PROVIDERS, Relationships.ORIGIN]
            # Sending to customers
            propagate_to == Relationships.CUSTOMERS
            # subprefix or non routed (don't send blackholes for prefixes)
            and (not ann.roa_valid_length or not ann.roa_routed)
        )
