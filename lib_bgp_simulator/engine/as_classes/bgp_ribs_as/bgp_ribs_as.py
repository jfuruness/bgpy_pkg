from typing import List, Optional

from ..bgp_as import BGPAS

from ...ann_containers import RIBsIn
from ...ann_containers import RIBsOut
from ...ann_containers import SendQueue

from ....announcements import Announcement as Ann
from ....engine_input import EngineInput
from ....enums import Relationships


class BGPRIBsAS(BGPAS):
    __slots__ = tuple()

    def __init__(self, *args, **kwargs):
        super(BGPRIBsAS, self).__init__(*args, **kwargs)
        self._ribs_in = RIBsIn()
        self._ribs_out = RIBsOut()
        self._send_q = SendQueue()

    # Propagation functions
    from .propagate_funcs import _propagate
    from .propagate_funcs import _policy_propagate
    from .propagate_funcs import _process_outgoing_ann
    from .propagate_funcs import _send_anns

    # Must add this func here since it refers to BGPRIBsAS
    # Could use super but want to avoid additional func calls
    def _populate_send_q(self,
                         propagate_to: Relationships,
                         send_rels: List[Relationships]):
        # Process outging ann is oerriden so this just adds to send q
        super(BGPRIBsAS, self)._propagate(propagate_to, send_rels)

    # Process incoming funcs
    from .process_incoming_funcs import process_incoming_anns
    from .process_incoming_funcs import _process_incoming_withdrawal
    from .process_incoming_funcs import _withdraw_ann_from_neighbors
    from .process_incoming_funcs import _select_best_ribs_in

    # Must be here since it referes to BGPRIBsAS
    # Could just use super but want to avoid the additional func calls
    def receive_ann(self, ann: Ann):
        super(BGPRIBsAS, self).receive_ann(ann, accept_withdrawals=True)
